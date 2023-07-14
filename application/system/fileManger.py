import base64
import json
import time
from datetime import datetime
import requests
from Crypto.Cipher import AES
from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Api, Resource
from application import db
from application.account import login_authority
from application.account.login_authority import token_auth
from application.conf.configuration import bucket_is_exit_url, create_bucket_url, upload_url, delete_url, downLoad_url, \
    appSecret, appId

collection = db["file"]
file = Blueprint("file", __name__, url_prefix="/api/v1/file")
api = Api(file)
log = db["log"]
interfaceCase = db["interfaceCase"]
uiCase = db["uiCase"]


# 新增文件
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
                 "optModule": "文件管理", "message": "添加文件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "文件管理", "message": "添加文件", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="新增失败")


def pkcs7padding(text):
    # 明文使用PKCS7填充，padding：凑篇幅的文字
    need_size = 16
    text_length = len(text)
    bytes_length = len(text.encode('utf-8'))
    padding_size = text_length if (bytes_length == text_length) else bytes_length
    padding = need_size - padding_size % need_size
    padding_text = chr(padding) * padding
    return text + padding_text


def AES_Encryption(secret_key, text):
    # AES加密 ,python运行处理的是 unicode码，因此，在做编码转换时，通常需要以unicode作为中间编码
    text = pkcs7padding(text)
    aes = AES.new(secret_key.encode("utf-8"), AES.MODE_ECB)
    en_text = aes.encrypt(text.encode('utf-8'))
    result = str(base64.b64encode(en_text), encoding='utf-8')
    return result


def request_head():
    # 生成文件服务器要求的请求头
    timestamp = int(time.time())
    timestamp *= 1000
    unencrypted_sign = str({"appId": appId, "timestamp": str(timestamp)})
    sign = AES_Encryption(appSecret, unencrypted_sign)
    headers = {"appId": appId, "sign": sign}
    return headers


# 上传文件
class Upload(Resource):
    def post(self):
        headers = request_head()
        # 先判断文件桶是否存在
        bucket_data = {"bucketName": "test_platform"}
        bucket_exit = requests.request(method="post", url=bucket_is_exit_url, json=bucket_data, headers=headers)
        # 如果存在直接上传，不存在就先创建文件桶
        if json.loads(bucket_exit.text)["data"]:
            file1 = request.files["file"]
            file_upload = requests.request(method="post", url=upload_url,
                                           files={"objectFile": (file1.filename, file1.stream)}, data=bucket_data,
                                           headers=headers)
            resourceId = json.loads(file_upload.text)["data"]["objectId"]
        else:
            requests.request(method="post", url=create_bucket_url, json=bucket_data, headers=headers)
            file1 = request.files["file"]
            file_upload = requests.request(method="post", url=upload_url,
                                           files={"objectFile": (file1.filename, file1.stream)}, data=bucket_data,
                                           headers=headers)
            resourceId = json.loads(file_upload.text)["data"]["objectId"]
        data = {"id": resourceId, "name": file1.filename}
        return dict(code=0, message="操作成功", data=data)


# 删除文件
class Delete(Resource):
    @token_auth
    def post(self):
        data = request.get_json()
        interface_case_name = []
        ui_case_name = []
        file_name = collection.find_one({"_id": ObjectId(data["id"])})["fileName"]

        interface_cases = interfaceCase.find({'json': file_name})
        for interface_case in interface_cases:
            interface_case_name.append(interface_case["caseName"])

        ui_cases = uiCase.find()
        for ui_case in ui_cases:
            if type(ui_case["testData"]) == dict:
                values = ui_case["testData"].values()
                for value in values:
                    if value == file_name:
                        ui_case_name.append(ui_case["caseName"])

        # 删除文件服务器上的文件，再删除库里的信息
        info = collection.find_one({"_id": ObjectId(data["id"])})
        delete_data = {"objectId": info["resourceId"], "bucketName": "test_platform"}
        headers = request_head()
        requests.request(method="post", url=delete_url, json=delete_data, headers=headers)
        result = collection.delete_one({"_id": ObjectId(data["id"])})
        count = result.deleted_count

        if count >= 0:
            log.insert_one(
                {"optUserId": login_authority.user_data["data"]["userId"],
                 "optUserName": login_authority.user_data["data"]["username"],
                 "optAccount": login_authority.user_data["data"]["account"],
                 "optModule": "文件管理", "message": "删除文件", "optTime": str(datetime.now()),
                 "ip": request.remote_addr, "optSuccess": "True",
                 "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
                 "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
            return dict(code=0, message="操作成功", warnings='接口' + str(interface_case_name) + "和" + 'UI' + str(ui_case_name)+"正在使用")
        log.insert_one(
            {"optUserId": login_authority.user_data["data"]["userId"],
             "optUserName": login_authority.user_data["data"]["username"],
             "optAccount": login_authority.user_data["data"]["account"],
             "optModule": "文件管理", "message": "删除文件", "optTime": str(datetime.now()),
             "ip": request.remote_addr, "optSuccess": "False",
             "roleId": login_authority.user_data["data"]["roleInfos"][0]["roleId"],
             "roleName": login_authority.user_data["data"]["roleInfos"][0]["roleName"]})
        return dict(code=1, messages="删除失败")


# 获取文件列表
class getList(Resource):
    @token_auth
    def post(self):
        page = request.json.get("page")
        pageSize = request.json.get("pageSize")
        fileName = request.json.get("fileName")
        fileType = request.json.get("fileType")
        query = {}
        if fileName:
            # 模糊查询，匹配区分大小写
            query["fileName"] = {"$regex": fileName, "$options": "i"}
        if fileType:
            query["fileType"] = fileType
        # 跳过前N条记录，限制只展示pagesize条记录
        results = collection.find(query).skip((page - 1) * pageSize).limit(pageSize)
        data = [{"id": str(result["_id"]), "fileName": result["fileName"], "fileType": result["fileType"],
                 "desc": result["desc"], "resourceId": result["resourceId"],
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


# 用于选择文件时的下拉框
class dropDown_file(Resource):
    @token_auth
    def post(self):
        droDdownFile = []
        for result in collection.find():
            result1 = {
                "value": str(result["_id"]),
                "label": result["fileName"]
            }
            droDdownFile.append(result1)
        return dict(code=0, data=droDdownFile)


# 获取下载地址
class getDownLoad(Resource):
    def post(self):
        objectId = request.json.get("objectId")
        headers = request_head()
        download_data = {"objectId": objectId, "bucketName": "test_platform"}
        download_address = requests.request(method="post", url=downLoad_url, json=download_data, headers=headers)
        data = json.loads(download_address.text)
        return dict(code=0, data=data["data"])


api.add_resource(Add, "/addFile", endpoint="addFile")
api.add_resource(Upload, "/upload", endpoint="upload")
api.add_resource(Delete, "/deleteFile", endpoint="deleteFile")
api.add_resource(getList, "/getfileList", endpoint="getfileList")
api.add_resource(dropDown_file, "/dropDownFileList", endpoint="dropDownFileList")
api.add_resource(getDownLoad, "/getDownLoadAddress", endpoint="getDownLoadAddress")
