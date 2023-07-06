import json
from application.common.utils import Util


class OperateJson:
    # 处理文件路径名，将需要的内容取出，保存为json对象
    def __init__(self, pn=None, fn=None):
        if fn:
            # 如果传入的路径包含header.json，将文件路径作为本类属性
            if 'header.json' in fn:
                self.path = fn
            # 不包含header.json，则需要拿到yaml文件中的包路径，拼接上传入的路径名，作为本类属性
            else:
                self.path = Util.get_conf()['dataJsonDir'] + pn + "/" + fn + '.json'
        else:
            # 如果不携带path，使用默认的文件的路径
            self.path = Util.get_conf()['dataJsonDir'] + 'default.json'
        # 以json对象的形式来保存测试数据
        self.data = self.read_data()

    # 读取数据
    def read_data(self):
        # 以utf8编码模式打开本类路径，并更名f
        with open(self.path, encoding='utf8') as f:
            # 读取json格式的文件f，将文件f中的数据转换为字典类型
            return json.load(f)

    # 根据键获取值
    def get_value(self, key):
        # 通过json对象的键获取对应的值并返回
        return self.data[key]

