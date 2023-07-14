from flask import Blueprint, request
from flask_restful import Api, Resource

from application import db
from application.account.login_authority import token_auth

collection = db["log"]
log = Blueprint("log", __name__, url_prefix="/api/v1/logs")
api = Api(log)


# 获取日志列表
class Getlist(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        query = {}
        # 跳过前N条记录，限制只展示pagesize条记录，倒序排序
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize).sort(
            [("_id", -1)])
        data = [{"id": str(result["_id"]), "optUserId": result["optUserId"], "optUserName": result["optUserName"],
                 "optAccount": result["optAccount"],
                 "optModule": result["optModule"], "message": result["message"], "optTime": result["optTime"],
                 "ip": result["ip"], "optSuccess": result["optSuccess"],
                 "roleId": result["roleId"], "roleName": result["roleName"]
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


api.add_resource(Getlist, "/getLogList", endpoint="getLogList")
