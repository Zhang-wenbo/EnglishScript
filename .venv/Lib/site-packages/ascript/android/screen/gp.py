import sys
from abc import ABC, abstractmethod
import numpy as np
from ascript.android import screen
from ascript.android.screen import gp_tool
from airscript.system import R as asR
from ascript.android.system import R
from ascript.android import plug
import importlib
import json
import cv2
import os


class Result:
    def __init__(self, image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None):
        self.image = image
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.data = data


class GPTask(ABC):
    name = "插件名称"
    ui_path = "插件UI地址"

    @abstractmethod
    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        pass


class GPStack:

    @staticmethod
    def run_json(json_param: str):
        # print(json_param)
        pass

    def __init__(self, cv_image: np.ndarray = None):
        super().__init__()
        self.gp_dao = []
        self.image = cv_image
        self.offset_x = 0
        self.offset_y = 0
        if self.image is None:
            self.image = screen.bitmap_to_cvimage()

    def add(self, dao: GPTask):
        self.gp_dao.append(dao)

    @staticmethod
    def change_img_channal(cv_image):
        dims = len(cv_image.shape)
        if dims == 2:
            # 图像是单通道的（可能是灰度或二值）
            channels = 1
        elif dims == 3:
            # 图像是多通道的（可能是BGR等）
            channels = cv_image.shape[2]

        if channels == 1:
            # 图像是单通道的，可能是二值图像或灰度图像
            # 检查像素值范围来区分二值图像和灰度图像
            # if np.all(cv_image >= 0) and np.all(cv_image <= 1):
            #     # 这是二值图像，像素值在0和1之间
            #     # 将其转换为8位无符号整数（0-255）的灰度图像
            #     image = (cv_image * 255).astype('uint8')
            #     # 不论是二值图像还是灰度图像，都转换为RGB图像
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2BGR)
        elif channels == 3:
            # 图像已经是RGB图像，无需转换
            pass

        return cv_image

    def run(self) -> Result:
        result = Result(self.image, 0, 0, None)
        for dao in self.gp_dao:
            result.image = GPStack.change_img_channal(result.image)
            result = dao.run(result.image, result.offset_x, result.offset_y, result.data)

        return result


### 图像处理插件

def gp_list():
    gp_cv_list = []
    gp_s_list = []


    gp_cv_list.append("ascript.android.screen.gp_tasks.Crop")
    gp_cv_list.append("ascript.android.screen.gp_tasks.GrayImage")
    gp_cv_list.append("ascript.android.screen.gp_tasks.Threshold")
    gp_cv_list.append("ascript.android.screen.Eraser")
    gp_cv_list.append("ascript.android.screen.gp_tasks.GaussianBlur")
    gp_cv_list.append("ascript.android.screen.gp_tasks.Erode")
    gp_cv_list.append("ascript.android.screen.gp_tasks.Dilate")
    gp_cv_list.append("ascript.android.screen.gp_tasks.MorphOpen")
    gp_cv_list.append("ascript.android.screen.gp_tasks.MorphClose")

    gp_s_list.append("ascript.android.screen.FindColors")
    gp_s_list.append("ascript.android.screen.CompareColors")
    gp_s_list.append("ascript.android.screen.Colors")
    gp_s_list.append("ascript.android.screen.FindImages")
    gp_s_list.append("ascript.android.screen.Ocr")
    gp_s_list.append("ascript.android.screen.OcrX")
    gp_s_list.append("ascript.android.screen.gp_tasks.Canny")
    gp_s_list.append("ascript.android.screen.gp_tasks.CvFontLib")
    gp_s_list.append("ascript.android.screen.CodeScanner")

    class_list = []

    for gp_s in gp_cv_list:
        module_name, class_name = gp_s.rsplit('.', 1)
        module = gp_tool.load_or_reload_module(module_name)
        gp_class = getattr(module, class_name)
        dao = {"name": gp_class.name, "ui_path": gp_class.ui_path, "id": gp_s, "class_name": class_name, "type": "OpenCV工具"}
        class_list.append(dao)

    for gp_s in gp_s_list:
        module_name, class_name = gp_s.rsplit('.', 1)
        module = gp_tool.load_or_reload_module(module_name)
        gp_class = getattr(module, class_name)
        dao = {"name": gp_class.name, "ui_path": gp_class.ui_path, "id": gp_s, "class_name": class_name, "type": "图色工具"}
        class_list.append(dao)

    try:
        gp_module_list = list(asR.get_screen_plugs())
        gp_plugs = json.loads(asR.get_screen_line_plugs())
        for gp_s in gp_module_list:
            module_name, class_name = gp_s.rsplit('.', 1)
            module = gp_tool.load_or_reload_module(module_name)
            gp_class = getattr(module, class_name)
            dao = {"name": gp_class.name, "ui_path": gp_class.ui_path, "id": gp_s, "class_name": class_name, "type": "调试工程"}
            class_list.append(dao)

        if len(gp_plugs) > 0:
            import airscript_frame

        for key, value in gp_plugs.items():
            print(key, value)
            plug.load(key)
            for gp_s in value:
                module_name, class_name = gp_s.rsplit('.', 1)
                module = gp_tool.load_or_reload_module(module_name)
                gp_class = getattr(module, class_name)
                dao = {"name": gp_class.name, "ui_path": gp_class.ui_path, "id": gp_s, "class_name": class_name,
                       "type": "云端插件", "nv": key}
                class_list.append(dao)
    except Exception as e:
        print(e)

    return class_list


def gp_list_json():
    return json.dumps(gp_list())


def run(gp_file: str, cv_img=None):
    # if cv_img is None:
    #     cv_img = screen.bitmap_to_cvimage()
    target_name = os.path.basename(gp_file)
    target_name = os.path.splitext(target_name)[0]
    target_name = "as_gp_" + target_name
    try:
        module = sys.modules[target_name]
        # print(module)
    except KeyError:
        target_dir = R.sd("/airscript/gp/" + target_name)
        # 解压
        asR.unzip(gp_file, target_dir)
        module = importlib.import_module(target_name)

    return module.gp(cv_img)

    # #根据data 生成代码
    # gpdata_file = R.rel(target_dir,"data.gp")
    # with open(gpdata_file, 'r', encoding='utf-8') as file:
    #     content = file.read()
    # print(content)
