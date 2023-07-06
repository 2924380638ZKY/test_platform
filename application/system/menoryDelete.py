import os
import shutil
import time

from application import db

taskResult = db["taskResult"]
log = db["log"]


def delete_records():
    count = taskResult.count_documents({})
    # 如果记录数大于400，则删除100条记录
    if count > 400:
        docs_to_delete = taskResult.find({}, limit=100)
        for doc in docs_to_delete:
            result1 = taskResult.find_one({"_id": doc['_id']})
            url = result1['allureUrl']
            start_index = url.find("allure-report-")
            end_index = url.find("/", start_index)
            report_name = url[start_index:end_index]
            folder_path = 'application/report/'
            file_list = os.listdir(folder_path)
            if report_name in file_list:
                shutil.rmtree(os.path.join(folder_path, report_name))
            taskResult.delete_one({'_id': doc['_id']})
    count1 = log.count_documents({})
    # 如果记录数大于1000，则删除500条记录
    if count1 > 1000:
        docs_to_delete = log.find({}, limit=500)
        for doc in docs_to_delete:
            log.delete_one({'_id': doc['_id']})
    # 删除临时目录下的所有文件
    folder_path = 'application/file_storage/'
    file_list = os.listdir(folder_path)
    for file_name in file_list:
        os.remove(os.path.join(folder_path, file_name))
    # logs目录下的日志
    logs_path = 'application/logs/runlog.log'
    fileinfo = os.stat(logs_path)
    size = fileinfo.st_size
    if size >= 1048576:
        os.remove(logs_path)


def auto_task():
    while True:
        # 调用 delete_records 方法
        delete_records()
        time.sleep(300)  # 休眠五分钟


def create_thread():
    # 启动自动调用任务线程
    from threading import Thread
    t = Thread(target=auto_task)
    t.start()


