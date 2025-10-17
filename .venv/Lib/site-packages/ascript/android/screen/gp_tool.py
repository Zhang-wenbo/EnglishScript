import json
import uuid

import cv2
import importlib
import os
from . import gp
from ascript.android import screen
from ascript.android.system import R
import importlib
import sys

str_header = []
str_body = []
str_stack_name = "gp_stack"
gp_result = None


def loadfrom_json(json_str, c_img, gp_name):
    job_data = json.loads(json_str)
    global str_header, str_body
    str_header = []
    str_body = []
    # cv_img = screen.bitmap_to_cvimage(c_img)

    str_header.append("from ascript.android.screen.gp import GPStack")
    str_header.append("import cv2")
    str_header.append("from ascript.android.system import R")
    str_header.append("from ascript.android import plug")
    str_body.append("def gp(cv_img=None):")
    # str_body.append(f"  cv_img = cv2.imread('{c_img}')")
    str_body.append(f"  {str_stack_name} = GPStack(cv_img)")

    # 组装job
    for gp in job_data:
        create_gpcode_with_dict(gp)

    str_body.append(f"  gp_result = {str_stack_name}.run()")
    str_body.append(f"  return gp_result")

    str_body.append(f"# 如需运行,取消以下代码注释")
    str_body.append(f"# res = gp()")
    str_body.append(f"# print(res.data)")

    final_code = '\n'.join(str(item) for item in str_header + str_body)
    print(final_code)
    # exec(final_code, globals())
    # 创建 init 文件,并写入数据.
    init_py_file = f"sdcard/airscript/gp/{gp_name}/__init__.py"

    if not os.path.exists(os.path.dirname(init_py_file)):
        os.makedirs(os.path.dirname(init_py_file))

    with open(init_py_file, 'w', encoding='utf-8') as file:
        file.write(final_code)

    cv_img = cv2.imread(c_img)
    gp_result = load_or_reload_module(gp_name).gp(cv_img)

    img_path = f"sdcard/airscript/screen/gp/{uuid.uuid4()}.jpg"
    # 提取目录部分
    directory = os.path.dirname(img_path)

    # 检查目录是否存在
    if not os.path.exists(directory):
        # 如果目录不存在，则创建它
        os.makedirs(directory)

    cv2.imwrite(img_path, gp_result.image)
    # print(gp_result.data)
    res = {"image": img_path, "offset_x": gp_result.offset_x, "offset_y": gp_result.offset_y, "data": gp_result.data}
    return json.dumps(res)
    # return res


def load(gpdir: str, cv_img=None):
    gpdata_file = R.rel(gpdir, "data.gp")


def load_or_reload_module(module_name_str):
    try:
        # 尝试从sys.modules中获取模块对象
        module = sys.modules[module_name_str]
        # 如果模块已经存在，则重新加载它
        print(f"Module {module_name_str} already loaded. Reloading...")
        module = importlib.reload(module)
    except KeyError:
        # 如果模块不存在，则导入它
        print(f"Module {module_name_str} not loaded. Importing...")
        module = importlib.import_module(module_name_str)
    return module


def create_gpcode_with_dict(gp):
    jobid = gp["id"]
    jobtype = gp["type"]
    jobnv = gp["nv"]
    jobdata = None
    if "data" in gp:
        jobdata = gp["data"]
    module_name, class_name = jobid.rsplit('.', 1)
    module = importlib.import_module(module_name)
    gp_class = getattr(module, class_name)
    if gp_class:
        # 存在这个类
        global str_header, str_body
        if "云端" in jobtype:
            str_header.append(f"plug.load('{jobnv}')")
        str_header.append(f"from {module_name} import {class_name}")
        str_body.append(f"  {str_stack_name}.add({class_name}({gptask_params(jobdata)}))")


def gptask_params(data):
    if "params" in data:
        return data["params"]
    else:
        return ""
