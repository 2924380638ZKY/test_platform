from datetime import datetime
from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource
from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["interface"]
interface = Blueprint("interface", __name__, url_prefix="/api/v1/interface")
api = Api(interface)
log = db["log"]


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["lastModifiedTime"] = str(datetime.now())
        data["lastModifiedBy"] = "admin"
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "接口管理", "message": "添加接口", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "接口管理", "message": "添加接口", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"interfaceName": data["interfaceName"],
                                                 "abilityModelId": data["abilityModelId"],
                                                 "method": data["method"], "url": data["url"],
                                                 "desc": data["desc"],
                                                 "lastModifiedTime": str(datetime.now()), "lastModifiedBy": "admin"}})
        count = result.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "接口管理", "message": "编辑接口", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "接口管理", "message": "编辑接口", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="编辑失败")


class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        interfaceCase = db["interfaceCase"]
        used_in_interfaceCase = interfaceCase.find_one({"interfaceId": data["id"]})
        if used_in_interfaceCase:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "接口管理", "message": "删除接口", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=2, message="该接口正在使用，删除失败")
        else:
            result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "接口管理", "message": "删除接口", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "接口管理", "message": "删除接口", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="删除失败")


class Get(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.find_one({"_id": ObjectId(data["id"])})
        if result is not None:
            result1 = {"id": str(result["_id"]), "abilityModelId": result["abilityModelId"],
                       "interfaceName": result["interfaceName"], "method": result["method"], "desc": result["desc"],
                       "url": result["url"], "lastModifiedTime": result["lastModifiedTime"], "lastModifiedBy": "admin"}
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        abilityModelId = request.json.get("abilityModelId")
        interfaceName = request.json.get("interfaceName")

        query = {}
        if abilityModelId:
            if len(abilityModelId) == 1:
                query["abilityModelId"] = abilityModelId[0]
            elif len(abilityModelId) == 2:
                query["abilityModelId"] = {"$all": abilityModelId[:2]}
            else:
                query["abilityModelId"] = abilityModelId
        if interfaceName:
            query["interfaceName"] = {"$regex": interfaceName, "$options": "i"}  # 模糊查询，匹配区分大小写
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        data = [{"id": str(result["_id"]), "abilityModelId": result["abilityModelId"],
                 "interfaceName": result["interfaceName"],
                 "url": result["url"],
                 "method": result["method"],
                 "desc": result["desc"],
                 "lastModifiedTime": result["lastModifiedTime"], "lastModifiedBy": result["lastModifiedBy"]
                 } for result in results]
        total_count = collection.count_documents(query)
        total_page = (total_count + pageSize - 1) // pageSize
        response_data = {
            "currentPage": page,
            "currentPageSize": pageSize,
            "totalPage": total_page,
            "totalCount": total_count,
            "dataList": data
        }
        return dict(code=0, message="操作成功", data=response_data)


class dropDown(Resource):
    @token_auth
    def post(self):
        abilityModelId = request.json.get("abilityModelId")
        query = {}
        if abilityModelId:
            if len(abilityModelId) == 1:
                query["abilityModelId"] = abilityModelId[0]
            elif len(abilityModelId) == 2:
                query["abilityModelId"] = {"$all": abilityModelId[:2]}
            else:
                query["abilityModelId"] = abilityModelId
        results = collection.find(query)
        data = [{"id": str(result["_id"]), "interfaceName": result["interfaceName"]
                 } for result in results]
        return dict(code=0, message="操作成功", data=data)


api.add_resource(Add, "/addInterface", endpoint="addInterface")
api.add_resource(Edit, "/editInterface", endpoint="editInterface")
api.add_resource(Delete, "/deleteInterface", endpoint="deleteInterface")
api.add_resource(Get, "/getInterfaceInfo", endpoint="getInterfaceInfo")
api.add_resource(Getlist, "/getInterfaceList", endpoint="getInterfaceList")
api.add_resource(dropDown, "/dropDownList", endpoint="dropDownList")
