from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource

from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["kit"]
kit = Blueprint("kit", __name__, url_prefix="/api/v1/kit")
api = Api(kit)
log = db["log"]
task = db['task']
interfaceCase = db["interfaceCase"]
uiCase = db["uiCase"]


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["caseList"] = []
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试套件管理", "message": "添加测试套件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "测试套件管理", "message": "添加测试套件", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"kitName": data["kitName"], "kitType": data["kitType"],
                                                 "desc": data["desc"]
                                                 }})
        count = result.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试套件管理", "message": "编辑测试套件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "测试套件管理", "message": "编辑测试套件", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="编辑失败")


class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        used_in_task = task.find_one({"kitId": data["id"]})
        if used_in_task:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试套件管理", "message": "删除测试套件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=11, message="该套件正在被任务使用，删除失败")

        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试套件管理", "message": "删除测试套件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "测试套件管理", "message": "删除测试套件", "optTime": str(datetime.now()),
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
            result1 = {"id": str(result["_id"]), "kitType": result["kitType"],
                       "kitName": result["kitName"], "desc": result["desc"], }
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        kitType = request.json.get("kitType")
        query = {}
        if kitType:
            query["kitType"] = kitType
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        data = [{"id": str(result["_id"]), "kitName": result["kitName"], "desc": result["desc"],
                 "kitType": result["kitType"]
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


class addCase(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        # idlist = []
        # for x in data["caseList"]:
        #     idlist.append(x["id"])
        result = collection.find_one({"_id": ObjectId(data["id"])})
        if result is not None:
            collection.update_one({"_id": ObjectId(data["id"])},
                                  {"$set": {"caseList": data["caseList"]}})
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试套件管理", "message": "编辑测试套件里的用例", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "测试套件管理", "message": "编辑测试套件里的用例", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="添加失败")


class allCase(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        abilityModelId = request.json.get("abilityModelId")
        caseName = request.json.get("caseName")
        priority = request.json.get("priority")
        query = {}
        if abilityModelId:
            if len(abilityModelId) == 1:
                query["abilityModelId"] = abilityModelId[0]
            elif len(abilityModelId) == 2:
                query["abilityModelId"] = {"$all": abilityModelId[:2]}
            else:
                query["abilityModelId"] = abilityModelId
        if caseName:
            query["caseName"] = {"$regex": caseName, "$options": "i"}  # 模糊查询，匹配区分大小写
        if priority or priority == 0:
            query["priority"] = priority
        if data["kitType"] == 1:
            abilityCase = db["abilityCase"]
            result1 = abilityCase.find(query)
            data = [
                {"id": str(result["_id"]), "abilityModelId": result["abilityModelId"], "caseName": result["caseName"],
                 "priority": result["priority"], "preconditions": result["preconditions"],
                 "testingProcedure": result["testingProcedure"],
                 "testData": result["testData"], "expectResult": result["expectResult"]
                 } for result in result1]
            return dict(code=0, data=data)
        elif data["kitType"] == 2:
            result2 = uiCase.find(query)
            data = [
                {"id": str(result["_id"]), "abilityModelId": result["abilityModelId"], "login": result["login"],
                 "caseName": result["caseName"],
                 "priority": result["priority"], "eventStep": result["eventStep"], "eventName": result["eventName"],
                 "testData": result["testData"],
                 "expectResult": result["expectResult"]
                 } for result in result2]
            return dict(code=0, data=data)
        elif data["kitType"] == 3:
            result3 = interfaceCase.find(query)
            data = [
                {"id": str(result["_id"]), "useToken": result["useToken"], "abilityModelId": result["abilityModelId"],
                 "caseName": result["caseName"],
                 "interfaceId": result["interfaceId"], "interfaceName": result["interfaceName"],
                 "priority": result["priority"],
                 "expectResult": result["expectResult"],
                 "testDataType": result["testDataType"], "json": result["json"],
                 "extractFields": result["extractFields"]
                 } for result in result3]
            return dict(code=0, data=data)
        else:
            return dict(code=1, message="输入数据有误")


class chooseCase(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.find_one({"_id": ObjectId(data["id"])})
        # case = {}
        if result is not None:
            case = result["caseList"]
            return dict(code=0, data=case)
            # if result["kitType"] == 3:
            #     if len(result["caseList"]) != 0:
            #         for x in result["caseList"]:
            #             print(x)
            #             result1 = interfaceCase.find_one({"_id": ObjectId(x)})
            #             case["id"] = x
            #             case["useToken"] = result1["useToken"]
            #             case["abilityModelId"] = result1["abilityModelId"]
            #             case["interfaceId"] = result1["interfaceId"]
            #             case["interfaceName"] = result1["interfaceName"]
            #             case["priority"] = result1["priority"]
            #             case["testDataType"] = result1["testDataType"]
            #             case["json"] = result1["json"]
            #             case["expectResult"] = result1["expectResult"]
            #             case["extractFields"] = result1["extractFields"]
        else:
            return dict(code=1, message="id错误")


api.add_resource(Add, "/addKit", endpoint="addKit")
api.add_resource(Edit, "/editKit", endpoint="editKit")
api.add_resource(Delete, "/deleteKit", endpoint="deleteKit")
api.add_resource(Get, "/getKitInfo", endpoint="getKitInfo")
api.add_resource(Getlist, "/getKitList", endpoint="getKitList")
api.add_resource(addCase, "/addCaseKit", endpoint="addCaseKit")
api.add_resource(allCase, "/showAllCase", endpoint="showAllCase")
api.add_resource(chooseCase, "/showChooseCase", endpoint="showChooseCase")
