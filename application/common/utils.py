import os
import yaml
from os import path
import logging.config


class Util:
    # 标记为类方法，可以通过类名调用
    @classmethod
    def get_conf(cls):
        # 以utf8编码模式打开本类路径并读取，并更名f
        with open('application/conf/conf.yaml', 'r', encoding='utf8') as f:
            # 将f的内容全部加载再转换为字典类型，赋给data
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data

    def screen_path_succ(self, item):
        screenshot_dir = "application/report/screen_capture"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        # 字符串格式化输出，{}代表内容
        screen_file = os.path.join(screenshot_dir, "成功{}.png".format(item.function.__name__))
        return screen_file

    def screen_path_fail(self, item):
        screenshot_dir = "application/report/screen_capture"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        # 字符串格式化输出，{}代表内容
        screen_file = os.path.join(screenshot_dir, "失败{}.png".format(item.function.__name__))
        return screen_file


# 将日志配置文件的路径赋值给conf_file,通过logging.config的方法将自己的日志配置上去
conf_file = Util.get_conf()['loggerConfigPath']
logging.config.fileConfig(conf_file)
logger = logging.getLogger()
