import datetime
import os
from datetime import datetime
from functools import wraps
from threading import Thread

import pytest
from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource

from application import db
from application.account import login_authority
from application.account.login_authority import token_auth

collection = db["task"]
task = Blueprint("task", __name__, url_prefix="/api/v1/task")
api = Api(task)
log = db["log"]
taskResult = db["taskResult"]
kit = db["kit"]
site = db['site']

depend_dicts = {}
use_data = {}


class Add(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        data["status"] = 2
        #  修改成多套件后，任务前端如何显示
        result = kit.find_one({"_id": ObjectId(data["kitId"])})
        data["kitName"] = result["kitName"]
        data_id = collection.insert_one(data).inserted_id
        if data_id is not None:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "任务管理", "message": "添加任务", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "任务管理", "message": "添加任务", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


class Edit(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        result = collection.update_one({"_id": ObjectId(data["id"])},
                                       {"$set": {"type": data["type"], "taskName": data["taskName"],
                                                 "kitId": data["kitId"], "desc": data["desc"]}})
        count = result.modified_count  # 影响的数据条数
        if count > 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "任务管理", "message": "编辑任务", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "任务管理", "message": "编辑任务", "optTime": str(datetime.now()),
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
                 "optModule": "任务管理", "message": "删除任务", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "任务管理", "message": "删除任务", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="删除失败")


class dropDown_kit(Resource):
    @token_auth
    def post(self):
        kitType = request.json.get("type")
        sum1 = []
        query = {}
        if type:
            query["kitType"] = kitType
        for result in kit.find(query):
            result1 = {
                "value": str(result["_id"]),
                "label": result["kitName"]
            }
            sum1.append(result1)
        return dict(code=0, data=sum1)


class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        type = request.json.get("type")
        taskName = request.json.get("taskName")
        kitName = request.json.get("kitName")
        query = {}
        if type:
            query["type"] = type
        if taskName:
            query["taskName"] = {"$regex": taskName, "$options": "i"}  # 模糊查询，匹配区分大小写
        if kitName:
            query["kitName  "] = kitName
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)  # 跳过前N条记录，限制只展示pagesize条记录
        data = [{"id": str(result["_id"]), "type": result["type"], "taskName": result["taskName"],
                 "kitName": result["kitName"], "kitId": result["kitId"],
                 "desc": result["desc"],
                 "status": result["status"],
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


def asyncz(f):
    @wraps(f)  # 元信息复制
    def wrapper(*args, **kwargs):  # 启用新线程
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


def get_test_message(data):
    test_task = collection.find_one({"_id": ObjectId(data["id"])})
    test_kit = kit.find_one({"_id": ObjectId(test_task["kitId"])})
    test_message = test_kit["caseList"]
    return test_message


@asyncz
def run_task(data, account_name):
    test_task = collection.find_one({"_id": ObjectId(data["id"])})
    test_site = site.find_one({"_id": ObjectId(data["webSiteName"])})
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    report_name = f'allure-report-{timestamp}'
    if not os.path.exists("application/report/" + report_name):
        os.makedirs("application/report/" + report_name)

    global depend_dicts
    if test_task["type"] == 2:  # UI
        pytest.main(
            ["application/task_ui/test_ui_task.py", "-vs", "--url", "http://" + test_site['webSiteIp'] + "/#/login",
             "--alluredir", "application/report/" + report_name + "/result", "--clean-alluredir"])
        os.system(
            "allure generate application/report/" + report_name + "/result -o application/report/" + report_name + "/allure --clean")
    elif test_task["type"] == 3:  # 接口
        pytest.main(
            ["application/task_interface/test_interface_task.py", "-vs", "--url", "http://" + test_site['webSiteIp'],
             "--alluredir", "application/report/" + report_name + "/result", "--clean-alluredir"])
        os.system(
            "allure generate application/report/" + report_name + "/result -o application/report/" + report_name + "/allure --clean")
    else:
        return dict(code=1, message="类型错误")
    taskResult.insert_one(
        {"taskType": test_task["type"], "taskName": test_task["taskName"], "webSiteName": test_site['webSiteIp'],
         "testResult": 0, "allureUrl": "10.1.40.72:5544/application/report/" + report_name + "/allure/index.html",
         "optUserId": account_name,
         "createTime": str(datetime.now())})
    collection.update_one({"_id": ObjectId(data["id"])}, {"$set": {"status": 2}})


class Run(Resource):
    @token_auth
    def post(self):
        global use_data
        use_data = request.get_json()
        collection.update_one({"_id": ObjectId(use_data["id"])},
                              {"$set": {"status": 1}})
        account_name = login_authority.user_data["data"]["account"]
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "任务管理", "message": "执行任务", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "True",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})

        run_task(use_data, account_name)
        return dict(code=0, message="操作成功")


api.add_resource(Add, "/addTask", endpoint="addTask")
api.add_resource(Edit, "/editTask", endpoint="editTask")
api.add_resource(Delete, "/deleteTask", endpoint="deleteTask")
api.add_resource(dropDown_kit, "/dropDownKitList", endpoint="dropDownKitList")
api.add_resource(Getlist, "/getTaskList", endpoint="getTaskList")
api.add_resource(Run, "/runTask", endpoint="runTask")
