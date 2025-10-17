import importlib
import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Any
from PIL import Image

from ascript.ios.developer.api import utils
from ascript.ios.developer.api.dao import ImgInout

str_stack_name = "strack"


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self):
        return json.dumps({
            "x": self.x,
            "y": self.y
        })


class GpInOut:

    def __init__(self, image: Image.Image = None, offset_x: int = 0, offset_y: int = 0, data: Any = None,
                 image_file: str = None, rect=None, skip_cache: bool = False):
        self.image = image
        self.image_file = image_file
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.data = data
        self.rect = rect
        self.skip_cache = skip_cache

        if image is None and image_file is None:
            self.image_file = "http://127.0.0.1:8100/screenshot"

    def img_inout(self) -> ImgInout:
        # 缓存逻辑
        if not self.skip_cache and utils.is_cache:
            # print('使用缓存',utils.is_cache)
            return ImgInout(rect=self.rect)

        # print('使用图片',self.skip_cache,utils.is_cache)

        return ImgInout(image=self.image, image_file=self.image_file, rect=self.rect)

    def __repr__(self):
        return json.dumps({
            "data": self.data
        }, cls=PointEncoder)


class GP(ABC):
    name = ""
    ui_path = ""

    @abstractmethod
    def run(self, gp_inout: GpInOut) -> GpInOut:
        pass


def gptask_params(data):
    if "params" in data:
        return data["params"]
    else:
        return ""


def load_or_reload_module(module_name_str):
    try:
        # 尝试从sys.modules中获取模块对象
        module = sys.modules[module_name_str]
        # 如果模块已经存在，则重新加载它
        # print(f"Module {module_name_str} already loaded. Reloading...")
        module = importlib.reload(module)
    except KeyError:
        # 如果模块不存在，则导入它
        # print(f"Module {module_name_str} not loaded. Importing...")
        module = importlib.import_module(module_name_str)
    return module


def create_gpcode_with_dict(gp):
    jobid = gp["id"]
    jobtype = gp["type"]
    # jobnv = gp["nv"]
    jobdata = None
    if "data" in gp:
        jobdata = gp["data"]
    module_name, class_name = jobid.rsplit('.', 1)
    module = importlib.import_module(module_name)
    gp_class = getattr(module, class_name)
    if gp_class:
        # 存在这个类
        global str_header, str_body
        # if "云端" in jobtype:
        #     str_header.append(f"plug.load('{jobnv}')")
        str_header.append(f"from {module_name} import {class_name}")
        str_body.append(f"  {str_stack_name}.append({class_name}({gptask_params(jobdata)}))")


def loadfrom_json(json_str, c_img, gp_name, gp_dir):
    # print(c_img)
    job_data = json.loads(json_str)
    global str_header, str_body
    str_header = []
    str_body = []
    # cv_img = screen.bitmap_to_cvimage(c_img)

    str_header.append("from PIL import Image")
    str_header.append("from ascript.ios.system import R")
    str_header.append("from ascript.ios.screen import GpInOut, capture")

    str_body.append("def gp(image):")
    # str_body.append(f"  cv_img = cv2.imread('{c_img}')")
    str_body.append(f"  strack = []")

    # 组装job
    for gp in job_data:
        create_gpcode_with_dict(gp)

    str_body.append(f"  inout = GpInOut(image_file=image,skip_cache=True)")
    str_body.append(f"  for gp in strack:")
    str_body.append(f"      inout = gp.run(inout)")
    # str_body.append(f"      print(inout)")
    str_body.append(f"  return inout")

    str_body.append(f"# 如需运行,取消以下代码注释")
    str_body.append(f"# res = gp()")
    str_body.append(f"# print(res.data)")

    final_code = '\n'.join(str(item) for item in str_header + str_body)
    # print(final_code)
    #
    # print(gp_dir)

    # 创建 init 文件,并写入数据.
    init_py_file = os.path.join(gp_dir, "__init__.py")
    if not os.path.exists(os.path.dirname(init_py_file)):
        os.makedirs(os.path.dirname(init_py_file))
    with open(init_py_file, 'w', encoding='utf-8') as file:
        file.write(final_code)

    module_name = os.path.basename(gp_dir)
    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = importlib.import_module(module_name)
    # gp_result = module.gp(Image.open(c_img))
    gp_result = module.gp(c_img)

    # 这是直接执行
    # exec(final_code, globals())
    # pil_img = Image.open(c_img)
    # gp_result = gprun(pil_img)

    """
    # img_path = f"sdcard/airscript/screen/gp/{uuid.uuid4()}.jpg"
    img_path = os.path.join(gp_dir, "temp.png")
    # 提取目录部分
    directory = os.path.dirname(img_path)

    # 检查目录是否存在
    if not os.path.exists(directory):
        # 如果目录不存在，则创建它
        os.makedirs(directory)

    gp_result.image.save(img_path)
    # cv2.(img_path, gp_result.image)
    # print(gp_result)
    """

    img_path = gp_result.image_file

    res = {"image": img_path, "offset_x": gp_result.offset_x, "offset_y": gp_result.offset_y, "data": gp_result.data}
    return json.dumps(res, cls=PointEncoder)


class PointEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Point):
            return {'x': obj.x, 'y': obj.y}
        # 让基本类处理不支持的类型
        return json.JSONEncoder.default(self, obj)
