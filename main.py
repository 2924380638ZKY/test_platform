from application import app
from application.case import abilityCase, model, event, uiCase, interface, kit  # 导入view类
from application.system import site, log, fileManger
from application.task import executeTask, taskResult
from application.system.menoryDelete import create_thread
import subprocess

# 定义命令
command = ['python', '-m', 'http.server', '5544']

if __name__ == '__main__':
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    create_thread()

    app.run('0.0.0.0', debug=False)



