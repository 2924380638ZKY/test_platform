from flask import Flask, jsonify, Blueprint
from pymongo import MongoClient


app = Flask(__name__)

# 连接MongoDB数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['test_platform']

from application.case.model import model
from application.case.abilityCase import abilityCase
from application.case.event import event
from application.case.uiCase import uiCase
from application.case.interface import interface
from application.case.interfaceCase import interfaceCase
from application.case.kit import kit
from application.system.site import site
from application.system.log import log
from application.system.fileManger import file
from application.task.executeTask import task
from application.task.taskResult import taskResult
from application.account.login import login

app.register_blueprint(model)
app.register_blueprint(abilityCase)
app.register_blueprint(event)
app.register_blueprint(uiCase)
app.register_blueprint(interface)
app.register_blueprint(interfaceCase)
app.register_blueprint(kit)
app.register_blueprint(site)
app.register_blueprint(log)
app.register_blueprint(file)
app.register_blueprint(task)
app.register_blueprint(taskResult)
app.register_blueprint(login)


