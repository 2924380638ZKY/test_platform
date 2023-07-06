import json
import os
import re
from time import sleep

import allure
import requests
from bson import ObjectId
from selenium.webdriver.common.by import By

from application import db
from application.common.utils import logger
from application.conf.configuration import platform_downLoad_url

event = db["event"]
file = db["file"]
account1 = ''
password1 = ''


class TestTask:

    def test_task(self, drivers, case, node_url):
        global account1
        global password1
        allure.dynamic.title(case["caseName"])
        allure.dynamic.severity(case["priority"])
        drivers.get(node_url)  # case:用例的信息
        count = 0
        if case['login']:
            drivers.implicitly_wait(120)
            drivers.get(node_url)
            drivers.find_element(By.XPATH, "//*[@id='app']/div/div[2]/form/div[2]/div/div/div/input").send_keys(
                account1)
            drivers.find_element(By.XPATH, "//*[@id='app']/div/div[2]/form/div[3]/div/div[1]/div/input").send_keys(
                password1)
            drivers.find_element(By.XPATH, "//*[@id='app']/div/div[2]/form/div[5]/div/button").click()
        for item in case["eventStep"]:
            event_data = event.find_one({"_id": ObjectId(item["eventId"])})
            for step_data in event_data["step"]:
                keyword = step_data['keyword']
                xpath = step_data['xpath']
                variable = step_data['variable']
                xpath = xpath[7:]
                if keyword == 'click':
                    element = drivers.find_element(By.XPATH, xpath)
                    element.click()
                    sleep(1)
                    logger.info("点击元素：{}".format(xpath))
                elif keyword == 'input':
                    element = drivers.find_element(By.XPATH, xpath)
                    element.clear()
                    if case['testData'][variable]:
                        element.send_keys(case['testData'][variable])
                        if variable == 'account':
                            account1 = case['testData'][variable]
                        elif variable == 'password':
                            password1 = case['testData'][variable]
                    else:
                        raise Exception("事件要求的输入名称和用例中的数据名称不符合")
                    sleep(1)
                    logger.info("输入文本：{}".format(case['testData'][variable]))
                elif keyword == 'upload':
                    element = drivers.find_element(By.XPATH, xpath)
                    file_data = file.find_one({"fileName": case['testData'][variable]})
                    downLoad = {"objectId": file_data["resourceId"]}
                    download_address = requests.request(method="post",
                                                        url=platform_downLoad_url,
                                                        json=downLoad)
                    if (json.loads(download_address.text)["data"]) is None:
                        raise Exception("没有找到该文件!")
                    download_response = requests.get(json.loads(download_address.text)["data"])
                    file_content = download_response.content
                    with open("application/file_storage/" + case['testData'][variable], 'wb') as f:
                        f.write(file_content)
                    absp = os.path.abspath("application/file_storage/" + case['testData'][variable])
                    element.send_keys(absp)
                    sleep(1)
                    count = count + 1
                    logger.info("上传文件：{}".format(case['testData'][variable]))
                else:
                    raise Exception("关键字keyword类型不存在!")
        if count == 0:
            sleep(1)
            result = re.search(case["expectResult"], drivers.page_source)
            logger.info("断言结果：{}".format(result))
            assert result
        else:
            sleep(10)
            result = re.search(case["expectResult"], drivers.page_source)
            logger.info("断言结果：{}".format(result))
            assert result
