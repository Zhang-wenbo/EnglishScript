import json
import os
from ascript.ios.developer.api import utils


def save(key: str, value, space=None):
    if space is None:
        space = utils.r_name

    file_path = os.path.join(utils.cache, "config.txt")
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # print('读取的数据',content)
            data = json.loads(content)
        # print('already', data)

    if space in data:
        data[space][key] = value
    else:
        data[space] = {}
        data[space][key] = value

    data_json = json.dumps(data)
    # print("数据", file_path, data_json)
    with open(file_path, 'w') as file:
        file.write(data_json)

    # try:
    #
    #
    # except Exception as e:
    #     print("错误", str(e))
    #     return False

    return True


def get(key: str, default=None, space=None):
    file_path = os.path.join(utils.cache, "config.txt")
    # print(file_path)
    if not os.path.exists(file_path):
        return default

    if space is None:
        space = utils.r_name

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(content)
            data = json.loads(content)
            res = data[space][key]
            return res
    except Exception as e:
        # 捕获其他可能的异常（如文件读取错误）
        print("错误:", str(e))
        os.remove(file_path)
        return default

    pass
