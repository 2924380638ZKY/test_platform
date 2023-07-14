import json
import os
from time import sleep

import allure
import requests
from bson import ObjectId

from application import db
from application.common.op_json import OperateJson
from application.common.utils import Util, logger
from application.conf.configuration import platform_downLoad_url
from application.task.executeTask import depend_dicts
from application.task_interface.parseDepend import Parsedepend

interface = db["interface"]
file = db["file"]
login_token = None


@allure.step("无需token的用例")
class WithoutToken:

    def withouttoken(self, content, node_url):
        global login_token
        allure.dynamic.title(content["caseName"])
        allure.dynamic.severity(content["priority"])
        test_interface = interface.find_one({"_id": ObjectId(content["interfaceId"])})
        test_url = node_url + test_interface["url"]
        if test_interface["method"] == 1:
            test_method = "get"
        elif test_interface["method"] == 2:
            test_method = "post"
        elif test_interface["method"] == 3:
            test_method = "delete"
        else:
            test_method = ""
        r = requests.request(method=test_method, url=test_url, json=content["json"])
        logger.info("请求地址:" + test_url)
        logger.info("请求体:" + str(content["json"]))
        rsp = r.text
        logger.info("返回体:" + rsp)
        if 'data' in json.loads(rsp):
            login_token = json.loads(rsp)["data"]["token"]
        elif 'userInfo' in json.loads(rsp):
            login_token = json.loads(rsp)["userInfo"]["token"]
        # 判断是否有被依赖字段
        if len(content["extractFields"]) != 0:
            # 解析返回值并填充到全局字典
            Parsedepend.parseDepend(r.text, content["extractFields"], depend_dicts)
        rsp = json.loads(rsp)
        logger.info("断言:" + str(content["expectResult"]))
        for key, value in (content["expectResult"]).items():
            assert rsp[key] == value


@allure.step("携带token的用例")
class WithToken:
    def __init__(self, token):
        # 将header.json中platformWithToken的值赋值给本类属性header
        self.header = OperateJson(None, Util.get_conf()["nodeHeaderJson"]).get_value("nodeWithToken")
        # 将本类属性header的两个值加上token，固定住。后续无需重复获取token
        self.header["Authorization"] = "Bearer " + token
        self.header["token"] = token

    def withtoken(self, content, node_url):
        allure.dynamic.title(content["caseName"])
        allure.dynamic.severity(content["priority"])
        if type(content["json"]) != str:
            for k, v in depend_dicts.items():
                x = eval(str(content["json"]).replace("{$" + k + "$}", v))
                content["json"] = x

        test_interface = interface.find_one({"_id": ObjectId(content["interfaceId"])})
        test_url = node_url + test_interface["url"]
        if test_interface["method"] == 1:
            test_method = "get"
        elif test_interface["method"] == 2:
            test_method = "post"
        elif test_interface["method"] == 3:
            test_method = "delete"
        else:
            test_method = ""
        headers = self.header
        if content["testDataType"] == 3:
            file_data = file.find_one({"fileName": content["json"]})

            if not file_data:
                raise Exception("没有叫这个名字的文件!")
            else:
                downLoad = {"objectId": file_data["resourceId"]}
                download_address = requests.request(method="post",
                                                    url=platform_downLoad_url,
                                                    json=downLoad)
                if (json.loads(download_address.text)["data"]) is None:
                    raise Exception("没有找到该文件!")

                download_response = requests.get(json.loads(download_address.text)["data"])
                file_content = download_response.content
                with open("application/file_storage/" + content['json'], 'wb') as f:
                    f.write(file_content)
                absp = os.path.abspath("application/file_storage/" + content['json'])
                filedatas = open(absp, 'rb')
                r = requests.request(method=test_method, url=test_url, headers=headers, files={"uploadfile": filedatas})
        else:
            r = requests.request(method=test_method, url=test_url, json=content["json"], headers=headers)
        logger.info("请求地址:" + test_url)
        logger.info("请求体:" + str(content["json"]))
        rsp = r.text
        logger.info("返回体:" + rsp)
        # 判断是否有被依赖字段
        if len(content["extractFields"]) != 0:
            Parsedepend.parseDepend(r.text, content["extractFields"], depend_dicts)
        rsp = json.loads(rsp)
        sleep(1)
        logger.info("断言:" + str(content["expectResult"]))
        for key, value in (content["expectResult"]).items():
            assert rsp[key] == value
