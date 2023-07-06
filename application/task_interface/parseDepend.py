import json


# 解析返回值并填充到全局字典
class Parsedepend:
    @classmethod
    def parseDepend(cls, rsp, depend_field, depend_dicts):

        for key, val in depend_field.items():
            tmp_res = json.loads(rsp)
            # logger.info("对响应结果进行提取！")
            if '.' in key:
                for v in key.split('.'):
                    if isinstance(tmp_res, dict):
                        tmp_res = tmp_res[v]
                        # logger.info(type(tmp_res))
                    # 若主字段不为列表，从字段为列表
                    elif isinstance(tmp_res, list):
                        tmp_res = tmp_res[0]
                        tmp_res = tmp_res[v]
                    elif isinstance(tmp_res, str):
                        # logger.info("该字段是字符串，进入第三个条件处理")
                        tmp_res = json.loads(tmp_res.replace('\\', ''))
                        tmp_res = tmp_res[v]
                    else:
                        # logger.info("该字段是其他类型，进入最后的条件处理")
                        tmp_res = tmp_res[v]
                if tmp_res:
                    depend_dicts[val] = tmp_res
                else:
                    depend_dicts[val] = '提取的值为空'
            else:
                if tmp_res[key]:
                    depend_dicts[val] = tmp_res[key]
                else:
                    depend_dicts[val] = '提取的值为空'
