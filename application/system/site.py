from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource

from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["site"]
site = Blueprint("site", __name__, url_prefix="/api/v1/webSite")
api = Api(site)
log = db["log"]


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "站点管理", "message": "添加站点", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "站点管理", "message": "添加站点", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"webSiteName": data["webSiteName"], "webSiteType": data["webSiteType"],
                                                 "webSiteIp": data["webSiteIp"],
                                                 "desc": data["desc"]}})
        count = result.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "站点管理", "message": "编辑站点", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "站点管理", "message": "编辑站点", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="编辑失败")


class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "站点管理", "message": "删除站点", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "站点管理", "message": "删除站点", "optTime": str(datetime.now()),
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
            result1 = {"id": str(result["_id"]), "webSiteName": result["webSiteName"],
                       "webSiteType": result["webSiteType"],
                       "webSiteIp": result["webSiteIp"],
                       "desc": result["desc"]}
            return dict(code=0, message="操作成功", data=result1)
        return dict(code=1, messages="获取信息失败")


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        webSiteName = request.json.get("webSiteName")
        webSiteType = request.json.get("webSiteType")
        query = {}
        if webSiteName:
            query["webSiteName"] = {"$regex": webSiteName, "$options": "i"}  # 模糊查询，匹配区分大小写
        if webSiteType:
            query["webSiteType"] = webSiteType
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        data = [{"id": str(result["_id"]), "webSiteName": result["webSiteName"], "webSiteType": result["webSiteType"],
                 "webSiteIp": result["webSiteIp"],
                 "desc": result["desc"]
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


class dropDown_site(Resource):
    @token_auth
    def post(self):
        sum = []
        for result in collection.find():
            result1 = {
                "value": str(result["_id"]),
                "label": result["webSiteIp"]
            }
            sum.append(result1)
        return dict(code=0, data=sum)


api.add_resource(Add, "/addWebSite", endpoint="addWebSite")
api.add_resource(Edit, "/editWebSite", endpoint="editWebSite")
api.add_resource(Delete, "/deleteWebSite", endpoint="deleteWebSite")
api.add_resource(Get, "/getWebSiteInfo", endpoint="getWebSiteInfo")
api.add_resource(Getlist, "/getwebSiteList", endpoint="getwebSiteList")
api.add_resource(dropDown_site, "/dropDownWebSiteList", endpoint="dropDownWebSiteList")
