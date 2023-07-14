import os
import shutil
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource

from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["taskResult"]
taskResult = Blueprint("taskResult", __name__, url_prefix="/api/v1/result")
api = Api(taskResult)
log = db["log"]
site = db["site"]


# 删除报告，同时删除对应目录下的报告文件
class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result1 = collection.find_one({"_id": ObjectId(data["id"])})
        if result1:
            url = result1['allureUrl']
            start_index = url.find("allure-report-")
            end_index = url.find("/", start_index)
            report_name = url[start_index:end_index]
            folder_path = 'application/report/'
            file_list = os.listdir(folder_path)
            if report_name in file_list:
                shutil.rmtree(os.path.join(folder_path, report_name))

        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "测试结果管理", "message": "删除测试结果", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "测试结果管理", "message": "删除测试结果", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="删除失败")


# 获取报告列表
class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        taskType = request.json.get("taskType")
        taskName = request.json.get("taskName")
        webSiteName = request.json.get("webSiteName")
        result = request.json.get("result")
        query = {}
        if taskType:
            query["taskType"] = taskType
        if taskName:
            # 模糊查询，匹配区分大小写
            query["taskName"] = {"$regex": taskName, "$options": "i"}
        if webSiteName:
            query["webSiteName"] = webSiteName
            query["webSiteName"] = site.find_one({"_id": ObjectId(query["webSiteName"])})["webSiteIp"]
        if result:
            query["result"] = result
        # 跳过前N条记录，限制只展示pagesize条记录
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize).sort(
            [("_id", -1)])
        data = [{"id": str(result["_id"]), "taskType": result["taskType"], "taskName": result["taskName"],
                 "webSiteName": result["webSiteName"], "allureUrl": result["allureUrl"],
                 "testResult": result["testResult"],
                 "optUserId": result["optUserId"], "createTime": result["createTime"]
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


api.add_resource(Delete, "/deleteResult", endpoint="deleteResult")
api.add_resource(Getlist, "/getResultList", endpoint="getResultList")
