import json
from functools import wraps

import requests
from flask import request
from requests.auth import HTTPBasicAuth
from application import db
from application.conf.configuration import clientId, clientSecret, checkToken, getToken, user_info

account = db['account']
user_data = {}


# token验证装饰器
def token_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # 获取请求头部的 Authorization 字段
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return {"code": 12, 'message': 'Token缺失'}
        global user_data
        # 获取 Authorization 字段中的 Token
        access_token = auth_header.split(' ')[1]
        auth = HTTPBasicAuth(clientId, clientSecret)
        # check token
        res = requests.post(checkToken + "?token=" + access_token, auth=auth)
        userInfo = requests.post(user_info + "?token=" + access_token, auth=auth)
        if json.loads(userInfo.text)['code'] == 0:
            user_data = json.loads(userInfo.text)
        # token 过期或者不合法
        if json.loads(res.text)['code'] != 0:
            token_is = account.find_one({"access_token": access_token})
            # 如果token不合法，并且在数据库里，进行refresh，刷新token，将token重新给前端
            if token_is:
                res1 = requests.post(getToken + "?grant_type=refresh_token&" + "refresh_token=" + token_is["refresh_token"], auth=auth)
                token_data = json.loads(res1.text)
                # 如果刷新失败，返回错误
                if token_data["code"] == 0:
                    account.update_one({"userId": token_data["data"]["userId"]},
                                       {"$set": {"access_token": token_data["data"]["access_token"],
                                                 "refresh_token": token_data["data"]["refresh_token"],
                                                 "expires_in": token_data["data"]["expires_in"]}})
                    return {"code": 13, 'message': 'Token刷新', "token": token_data["data"]["access_token"]}
                else:
                    return {"code": 14, 'message': 'Token不合法'}
            else:
                return {"code": 14, 'message': 'Token不合法'}
        return func(*args, **kwargs)

    return decorated
