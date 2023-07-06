from datetime import datetime
from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource
from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["model"]
model = Blueprint("model", __name__, url_prefix="/api/v1/model")
api = Api(model)
log = db["log"]
abilityCase = db["abilityCase"]
event = db["event"]
interface = db["interface"]
interfaceCase = db["interfaceCase"]
kit = db["kit"]
uiCase = db["uiCase"]


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["modelList"] = []
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "添加模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "模块管理", "message": "添加模块", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"modelName": data["modelName"], "desc": data["desc"]}})
        count = result.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "编辑模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "模块管理", "message": "编辑模块", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="编辑失败")


class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        used_in_abilityCase = abilityCase.find_one({"abilityModelId": data["id"]})
        if used_in_abilityCase:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=4, message="该模块在功能用例中已被使用，删除失败")

        used_in_interface = interface.find_one({"abilityModelId": data["id"]})
        if used_in_interface:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=5, message="该模块在接口中已被使用，删除失败")

        used_in_interfaceCase = interfaceCase.find_one({"abilityModelId": data["id"]})
        if used_in_interfaceCase:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=6, message="该模块在接口用例中已被使用，删除失败")

        used_in_event = event.find_one({"abilityModelId": data["id"]})
        if used_in_event:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=7, message="该模块在事件中已被使用，删除失败")

        used_in_uiCase = uiCase.find_one({"abilityModelId": data["id"]})
        if used_in_uiCase:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "False",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=8, message="该模块在UI用例中已被使用，删除失败")

        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "模块管理", "message": "删除模块", "optTime": str(datetime.now()),
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
            result1 = {"id": str(result["_id"]), "modelName": result["modelName"], "desc": result["desc"]}
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


class Maintain(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.find_one({"_id": ObjectId(data["id"])})
        if result is not None:
            collection.update_one({"_id": ObjectId(data["id"])},
                                  {"$set": {"modelName": data["modelName"], "desc": data["desc"],
                                            "modelList": data["modelList"]}})
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "模块管理", "message": "维护模块", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "模块管理", "message": "维护模块", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="维护失败")


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        query = {}
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        dataList = [{"id": str(result["_id"]), "modelName": result["modelName"], "desc": result["desc"],
                     "modelList": result["modelList"]
                     } for result in results]
        total_count = collection.count_documents(query)
        total_page = (total_count + pageSize - 1) // pageSize
        data = {"currentPage": page, "currentPageSize": pageSize, "totalCount": total_count, "totalPage": total_page,
                "dataList": dataList}
        return dict(code=0, message="操作成功", data=data)


class Transfer(Resource):
    @token_auth
    def post(self):
        models = []
        for model in collection.find():
            model_data = {
                "moduleId": str(model["_id"]),
                "moduleName": model["modelName"],
                "childrenList": []
            }
            for child in model["modelList"]:
                child_data = {
                    "moduleId": child["id"],
                    "moduleName": child["label"],
                    "childrenList": []
                }
                if "children" in child:
                    for grandchild in child["children"]:
                        grandchild_data = {
                            "moduleId": grandchild["id"],
                            "moduleName": grandchild["label"]
                        }
                        child_data["childrenList"].append(grandchild_data)
                model_data["childrenList"].append(child_data)
            models.append(model_data)
        return dict(code=0, message="操作成功", data=models)


class dropDown(Resource):
    @token_auth
    def post(self):
        models = []
        for model in collection.find():
            model_data = {
                "value": str(model["_id"]),
                "label": model["modelName"],
                "children": []
            }
            for child in model["modelList"]:
                child_data = {
                    "value": child["id"],
                    "label": child["label"],
                    "children": []
                }
                if "children" in child:
                    for grandchild in child["children"]:
                        grandchild_data = {
                            "value": grandchild["id"],
                            "label": grandchild["label"]
                        }
                        child_data["children"].append(grandchild_data)
                model_data["children"].append(child_data)
            models.append(model_data)
        return dict(code=0, message="操作成功", data=models)


api.add_resource(Add, "/addModel", endpoint="addModel")
api.add_resource(Edit, "/editModel", endpoint="editModel")
api.add_resource(Delete, "/deleteModel", endpoint="deleteModel")
api.add_resource(Get, "/getModelInfo", endpoint="getModelInfo")
api.add_resource(Maintain, "/maintainModel", endpoint="maintainModel")
api.add_resource(Getlist, "/getModelList", endpoint="getModelList")
api.add_resource(Transfer, "/transferData", endpoint="transferData")
api.add_resource(dropDown, "/dropDownList", endpoint="dropDownList")
