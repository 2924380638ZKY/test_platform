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


# 新增模块
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


# 编辑模块
class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"modelName": data["modelName"], "desc": data["desc"]}})
        # 影响的数据条数
        count = result.modified_count
        if count >= 0:
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


# 删除模块，如果模块有被使用，无法删除。现在顺序是按功能用例，接口，接口用例，事件，UI用例来。
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


# 获取某个模块的信息
class Get(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.find_one({"_id": ObjectId(data["id"])})
        if result is not None:
            result1 = {"id": str(result["_id"]), "modelName": result["modelName"], "desc": result["desc"]}
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


# 维护模块，维护模块的节点，如果节点被使用了，维护失败
class Maintain(Resource):
    @token_auth
    def post(self):
        # 获取原始的children_id列表和新的children_id列表，进行比较
        original_children_ids = []
        new_children_ids = []
        new_data = request.get_json()
        original_data = collection.find_one({"_id": ObjectId(new_data["id"])})
        for original_model in original_data['modelList']:
            for child in original_model['children']:
                original_children_ids.append(child['id'])
        for new_model in new_data['modelList']:
            for child in new_model['children']:
                new_children_ids.append(child['id'])
                
        # 如果这个原始id不在新的children列表里，并且这个原始id被使用了，返回维护失败
        for original_children_id in original_children_ids:
            used_in_abilityCase = abilityCase.find_one({"abilityModelId": original_children_id})
            if original_children_id not in new_children_ids and used_in_abilityCase:
                return dict(code=1, message="删除的子节点在功能用例中已被使用，维护失败")

            used_in_interface = interface.find_one({"abilityModelId": original_children_id})
            if original_children_id not in new_children_ids and used_in_interface:
                return dict(code=1, message="删除的子节点在接口中已被使用，维护失败")

            used_in_interfaceCase = interfaceCase.find_one({"abilityModelId": original_children_id})
            if original_children_id not in new_children_ids and used_in_interfaceCase:
                return dict(code=1, message="删除的子节点在接口用例中已被使用，维护失败")

            used_in_event = event.find_one({"abilityModelId": original_children_id})
            if original_children_id not in new_children_ids and used_in_event:
                return dict(code=1, message="删除的子节点在事件中已被使用，维护失败")

            used_in_uiCase = uiCase.find_one({"abilityModelId": original_children_id})
            if original_children_id not in new_children_ids and used_in_uiCase:
                return dict(code=1, message="删除的子节点在UI用例中已被使用，维护失败")

        # 上述情况都没有，正常维护
        result = collection.find_one({"_id": ObjectId(new_data["id"])})
        if result is not None:
            collection.update_one({"_id": ObjectId(new_data["id"])},
                                  {"$set": {"modelName": new_data["modelName"], "desc": new_data["desc"],
                                            "modelList": new_data["modelList"]}})
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


# 获取模块列表
class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        query = {}
        # 跳过前N条记录，限制只展示pagesize条记录
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  
        dataList = [{"id": str(result["_id"]), "modelName": result["modelName"], "desc": result["desc"],
                     "modelList": result["modelList"]
                     } for result in results]
        total_count = collection.count_documents(query)
        total_page = (total_count + pageSize - 1) // pageSize
        data = {"currentPage": page, "currentPageSize": pageSize, "totalCount": total_count, "totalPage": total_page,
                "dataList": dataList}
        return dict(code=0, message="操作成功", data=data)


# 模块用于查看时的信息数据返回
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


# 下拉框数据
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
