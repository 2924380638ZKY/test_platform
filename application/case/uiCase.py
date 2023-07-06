from datetime import datetime
from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource
from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["uiCase"]
uiCase = Blueprint("uiCase", __name__, url_prefix="/api/v1/uiCase")
api = Api(uiCase)
log = db["log"]
kit = db['kit']
event = db['event']


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["eventName"] = []
        for eventid in data["eventStep"]:
            result = event.find_one({"_id": ObjectId(eventid["eventId"])})
            data["eventName"].append(result["eventName"])
        data["lastModifiedTime"] = str(datetime.now())
        data["lastModifiedBy"] = "admin"
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "UI用例管理", "message": "添加UI用例", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "UI用例管理", "message": "添加UI用例", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["eventName"] = []
        for eventid in data["eventStep"]:
            result = event.find_one({"_id": ObjectId(eventid["eventId"])})
            data["eventName"].append(result["eventName"])
        result1 = collection.update_one({"_id": ObjectId(data["id"])},
                                        {"$set": {"abilityModelId": data["abilityModelId"], "login": data["login"],
                                                  "priority": data["priority"],
                                                  "caseName": data["caseName"], "eventStep": data["eventStep"],
                                                  "eventName": data["eventName"],
                                                  "testData": data["testData"], "expectResult": data["expectResult"],
                                                  "lastModifiedTime": str(datetime.now()), "lastModifiedBy": "admin"}})

        count = result1.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "UI用例管理", "message": "编辑UI用例", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "UI用例管理", "message": "编辑UI用例", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="编辑失败")


class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        used_in_kit = kit.find_one({"caseList.id": data["id"]})
        if used_in_kit:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "UI用例管理", "message": "删除UI用例", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=10, message="该UI用例正在被套件使用，删除失败")

        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "UI用例管理", "message": "删除UI用例", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "UI用例管理", "message": "删除UI用例", "optTime": str(datetime.now()),
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
                       "priority": result["priority"], "login": data["login"],
                       "caseName": result["caseName"], "eventStep": result["eventStep"],
                       "testData": result["testData"], "expectResult": result["expectResult"]}
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        abilityModelId = request.json.get("abilityModelId")
        caseName = request.json.get("caseName")
        priority = request.json.get("priority")
        query = {}
        if abilityModelId:
            if len(abilityModelId) == 1:
                query["abilityModelId"] = abilityModelId[0]
            elif len(abilityModelId) == 2:
                query["abilityModelId"] = {"$all": abilityModelId[:2]}
            elif len(abilityModelId) == 3:
                query["abilityModelId"] = abilityModelId
        if caseName:
            query["caseName"] = {"$regex": caseName, "$options": "i"}  # 模糊查询，匹配区分大小写
        if priority or priority == 0:
            query["priority"] = priority
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        data = [{"id": str(result["_id"]), "abilityModelId": result["abilityModelId"], "login": result["login"],
                 "caseName": result["caseName"],
                 "priority": result["priority"], "eventStep": result["eventStep"], "eventName": result["eventName"],
                 "testData": result["testData"],
                 "expectResult": result["expectResult"],
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


api.add_resource(Add, "/addUiCase", endpoint="addUiCase")
api.add_resource(Edit, "/editUiCase", endpoint="editUiCase")
api.add_resource(Delete, "/deleteUiCase", endpoint="deleteUiCase")
api.add_resource(Get, "/getUiCaseInfo", endpoint="getUiCaseInfo")
api.add_resource(Getlist, "/getCaseList", endpoint="getCaseList")
