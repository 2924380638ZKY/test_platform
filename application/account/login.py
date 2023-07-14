import json

import requests
from flask import Blueprint, request
from flask_restful import Api, Resource
from requests.auth import HTTPBasicAuth

from application import db
from application.conf.configuration import clientId, clientSecret, getToken, login_url, getCode, logout

login = Blueprint("login", __name__, url_prefix="/api/v1")
api = Api(login)
account = db['account']


# 返回授权的code到浏览器
class GetCode(Resource):
    def post(self):
        code = getCode + "?client_id=" + clientId + "&response_type=code&redirect_uri=" + login_url
        return dict(code=0, message=code)


# 进行登录，将登录成功后的信息保存到库里
class Login(Resource):
    def post(self):
        auth = HTTPBasicAuth(clientId, clientSecret)
        res = requests.post(getToken + "?grant_type=authorization_code&" + "code=" + request.json.get(
            "code") + "&redirect_uri=" + login_url, auth=auth)
        token_data = json.loads(res.text)
        if token_data["code"] == 0:
            result = account.find_one({"userId": (token_data["data"]["userId"])})
            if result:
                account.update_one({"userId": token_data["data"]["userId"]},
                                   {"$set": {"client_id": token_data["data"]["client_id"],
                                             "access_token": token_data["data"]["access_token"],
                                             "refresh_token": token_data["data"]["refresh_token"],
                                             "expires_in": token_data["data"]["expires_in"]}})
            else:
                account.insert_one(
                    {"userId": token_data["data"]["userId"], "client_id": token_data["data"]["client_id"],
                     "access_token": token_data["data"]["access_token"],
                     "refresh_token": token_data["data"]["refresh_token"],
                     "expires_in": token_data["data"]["expires_in"]})
            return dict(code=0, message="操作成功", data=json.loads(res.text)["data"])
        else:
            return dict(code=1, message="登录失败")


# 注销，退出登录
class Logout(Resource):
    def post(self):
        token = request.json.get("token")
        res = requests.post(logout + "?token=" + token)
        if json.loads(res.text)["code"] == 0:
            return dict(code=0, message="注销成功")
        else:
            return dict(code=1, message="注销失败")


api.add_resource(GetCode, "/account/getCode", endpoint="account/getCode")
api.add_resource(Login, "/account/login", endpoint="account/login")
api.add_resource(Logout, "/account/logout", endpoint="/account/logout")
