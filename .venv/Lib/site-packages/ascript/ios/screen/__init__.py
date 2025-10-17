import base64
import io
import threading
import time
import typing
from io import BytesIO
from typing import Union
from PIL import Image
from ascript.ios import system
from ascript.ios.developer.api import oc, oc_gp, utils, wda_gp
from ascript.ios.screen.color_tools import find_colors
from ascript.ios.screen.gp import GP, GpInOut
from ascript.ios.wdapy import Orientation

use_wda_gp = False


def is_cache():
    return utils.is_cache


def cache(_cache: bool, image: Image.Image = None, image_file: str = None):
    utils.is_cache = _cache

    if image is None and image_file is None and use_wda_gp:
        return wda_gp.screen_cache(_cache)

    oc_gp.screen_cache(_cache, GpInOut(image=image, image_file=image_file, skip_cache=True).img_inout())
    if not _cache:
        CompareColors.cache_img = None


def capture(rect=None) -> Image.Image:
    if system.client:
        image = system.client.screenshot()
        if rect:
            image = image.crop(rect)
        return image
    return None


def size() -> typing.Tuple[int, int]:
    if system.client:
        return system.client.window_size()
    return 0, 0


def ori() -> Orientation:
    if system.client:
        return system.client.get_orientation()
    return None


# 图片操作

def image_to_base64(image: Image.Image = None, image_file: str = None, image_format='PNG', decode: str = "utf-8"):
    """
    将Pillow的Image对象转换为Base64编码的字符串

    :param image: Pillow的Image对象
    :param image_format: 图片格式，默认为'PNG'
    :param image_file: 图片文件
    :param decode: base64 编码格式
    :return: 图片的Base64编码字符串
    """

    if image is None and image_file is None:
        image = capture()

    if image_file:
        with Image.open(image_file) as img:
            image = img

    buffered = BytesIO()
    # 将Image对象保存到字节流中
    image.save(buffered, format=image_format)
    # 获取字节流的二进制数据
    image_byte_arr = buffered.getvalue()
    # 对二进制数据进行Base64编码
    base64_str = base64.b64encode(image_byte_arr)
    # 将字节类型的Base64编码转换为UTF-8字符串
    return base64_str.decode(decode)


def image_read(file_path: str):
    return Image.open(file_path)


def image_save(image: Image.Image, path: str):
    image.save(path)


def image_crop(image: Image.Image, rect: tuple):
    return image.crop(rect)


def image_pixel(image: Image.Image, x: int, y: int):
    return image.getpixel((x, y))


def image_rotate(image: Image.Image, angle: int, expand: bool = True):
    return image.rotate(angle, expand=expand)


def image_compress(image: Image.Image, quality=50, _format='PNG'):
    output = io.BytesIO()
    image.save(output, format=_format, quality=quality)  # 设置JPEG质量为50%
    # 从BytesIO对象加载压缩后的图像
    compressed_image = Image.open(output)
    # 此时compressed_img是一个新的Image对象，包含了压缩后的图像数据
    # 注意：由于我们是从BytesIO对象加载的，所以原始指针在Image.open()后需要重置到开头
    output.seek(0)
    return compressed_image


class FindColors(GP):
    name = "多点找色"
    ui_path = "/static/gp/find_colors"

    def __init__(self, colors: str, rect: list = None, space: int = 5, ori: int = 2, diff: list = (5, 5, 5), num=-1,
                 image: Image.Image = None, image_file=None):
        self.colors = colors
        self.rect = rect
        self.space = space
        self.ori = ori
        self.diff = diff
        self.num = num
        self.image = image
        self.image_file = image_file
        self.gp = GpInOut(image=image, image_file=image_file, rect=rect)

    def thread_run(self, inout):
        inout.data = oc_gp.find_colors(inout.img_inout(), self.colors, self.space, self.ori, self.diff, self.num)

    def run(self, inout: GpInOut) -> GpInOut:
        inout.data = None
        inout.rect = self.rect

        if self.image is None and self.image_file is None and use_wda_gp:
            inout.data = wda_gp.find_colors(inout.img_inout(), self.colors, self.space, self.ori, self.diff, self.num)
            return inout

        threading.Thread(target=self.thread_run, args=(inout,)).start()
        while inout.data is None:
            time.sleep(0.001)
        # inout.data = oc_gp.find_colors(inout.img_inout(), self.colors, self.space, self.ori, self.diff, self.num)
        return inout

    def find_all(self):
        self.num = -1
        return self.run(self.gp).data

    def find(self):
        self.num = 1
        res = self.run(self.gp).data
        if len(res) > 0:
            return res[0]
        return None


class CompareColors(GP):
    name = "多点比色"
    ui_path = "/static/gp/compare_colors"
    cache_img = None

    def __init__(self, colors: str, diff: tuple = (5, 5, 5), image: Image.Image = None, image_file=None):
        self.colors = colors
        self.diff = diff
        self.image = image
        self.image_file = image_file
        self.gp = GpInOut(image=self.image, image_file=self.image_file)
        self.cache_img = None

    def run(self, gp_inout: GpInOut) -> GpInOut:
        img_inout = gp_inout.img_inout()
        if img_inout.image is None and img_inout.image_file is None:
            if CompareColors.cache_img is None:
                CompareColors.cache_img = capture()
            a_image = CompareColors.cache_img
        else:
            if img_inout.image_file and not img_inout.image_file.startswith("http"):
                a_image = image_read(gp_inout.image_file)
            elif img_inout.image:
                a_image = img_inout.image
            else:
                a_image = capture()

        colors = color_tools.ana_colors(self.colors)
        for color in colors:
            color2 = a_image.getpixel((color.x, color.y))
            if not color_tools.compare_color_n(color2, color.rgb, self.diff if color.diff is None else color.diff):
                gp_inout.data = False
                return gp_inout
        gp_inout.data = True
        return gp_inout

    def compare(self):
        return self.run(self.gp).data


class CountingColor(GP):
    name = "颜色数量"
    ui_path = "/static/gp/colors_num"

    def __init__(self, colors: str, rect: tuple = None, diff: tuple = (5, 5, 5), image: Image.Image = None,
                 image_file=None):
        self.colors = colors
        self.diff = diff
        self.rect = rect
        self.gp = GpInOut(image=image, image_file=image_file, rect=rect)

    def thread_run(self, inout: GpInOut):
        inout.data = oc_gp.counting_color(inout.img_inout(), colors=self.colors, diff=self.diff)

    def run(self, inout: GpInOut) -> GpInOut:
        # gp_inout.data = oc_gp.counting_color(gp_inout.img_inout(), colors=self.colors, diff=self.diff)
        inout.rect = self.rect
        inout.data = None

        if inout.image_file == "http://127.0.0.1:8100/screenshot" and use_wda_gp:
            inout.data = wda_gp.counting_color(inout.img_inout(), self.colors, self.diff)
            return inout

        threading.Thread(target=self.thread_run, args=(inout,)).start()
        while inout.data is None:
            time.sleep(0.01)
        return inout

    def find(self):
        return self.run(self.gp).data


class FindImages(GP):
    name = "找图"
    ui_path = "/static/gp/find_images"
    M_TEMPLATE = 0
    M_SIFT = 1
    M_MIX = 2

    @property
    def gp_inout(self):
        return self.gp

    def __init__(self, part_image: Union[str, list], rect: tuple = None, confidence=0.1, rgb: bool = True,
                 mode=M_TEMPLATE, num=0,
                 image: Image.Image = None, image_file: str = None):
        self.part_image = part_image
        self.rect = rect
        self.confidence = confidence
        self.mode = mode
        self.num = num
        self.rgb = rgb

        self.gp = GpInOut(image=image, image_file=image_file, rect=rect)

    def thread_run(self, inout):
        if self.mode == FindImages.M_TEMPLATE or self.mode == FindImages.M_MIX:
            inout.data = oc_gp.find_all_template(inout.img_inout(), self.part_image, threshold=self.confidence,
                                                 rgb=self.rgb,
                                                 max_res=self.num)

        if self.mode == FindImages.M_SIFT or self.mode == FindImages.M_MIX:
            if inout.data is None or len(inout.data) < 1:
                inout.data = oc_gp.find_sift(inout.img_inout(), self.part_image, threshold=self.confidence,
                                             rgb=self.rgb, max_res=self.num)

    def run(self, inout: GpInOut) -> GpInOut:
        # image.show()
        if type(self.part_image) is str:
            self.part_image = [self.part_image]

        inout.rect = self.rect

        inout.data = None
        threading.Thread(target=self.thread_run, args=(inout,)).start()
        while inout.data is None:
            time.sleep(0.01)

        # data = None
        # if self.mode == FindImages.M_TEMPLATE or self.mode == FindImages.M_MIX:
        #     data = oc_gp.find_all_template(gp_inout.img_inout(), self.part_image, threshold=self.confidence,
        #                                    rgb=self.rgb,
        #                                    max_res=self.num)
        #
        # if self.mode == FindImages.M_SIFT or self.mode == FindImages.M_MIX:
        #     if data is None or len(data) < 1:
        #         data = oc_gp.find_sift(gp_inout.img_inout(), self.part_image, threshold=self.confidence,
        #                                rgb=self.rgb, max_res=self.num)

        return inout

    def find(self):
        data = self.find_template()
        if data is None or len(data) < 1:
            data = self.find_sift()

        return data

    def find_all(self):
        data = self.find_all_template()
        if data is None or len(data) < 1:
            data = self.find_all_template()

        return data

    def find_template(self):
        self.num = 1
        self.mode = FindImages.M_TEMPLATE
        data = self.run(self.gp).data
        if data and len(data) > 0:
            data = data[0]

        return data

    def find_all_template(self):
        self.num = -1
        self.mode = FindImages.M_TEMPLATE
        return self.run(self.gp).data

    def find_sift(self):
        self.num = 1
        self.mode = FindImages.M_SIFT
        data = self.run(self.gp).data
        if data and len(data) > 0:
            data = data[0]

        return data

    def find_all_sift(self):
        self.num = -1
        self.mode = FindImages.M_SIFT
        return self.run(self.gp).data


class Ocr(GP):
    Tess_ENG = "eng"
    Tess_CHI = "chi"
    Tess_NUM = "num"
    RIL_AUTO = -1
    RIL_BLOCK = 0
    RIL_PARA = 1
    RIL_TEXTLINE = 2
    RIL_WORD = 3
    RIL_SYMBOL = 4
    lock = threading.Lock()
    name = "文字识别"
    ui_path = "/static/gp/ocr"

    MODE_MLK = 1
    MODE_PADDLE_V2 = 2
    MODE_PADDLE_V3 = 3
    MODE_TESS = 4

    def __init__(self, mode=MODE_MLK, rect=None, pattern: str = None, confidence: float = 0.1,
                 max_side_len: int = 1200, image: Image.Image = None, image_file: str = None):
        self.mode = mode
        self.rect = rect
        self.pattern = pattern
        self.confidence = confidence
        self.max_side_len = 1200

        self.gp = GpInOut(image=image, image_file=image_file, rect=rect)

    def thread_run(self, inout: GpInOut):
        inout.data = oc_gp.ocr(self.mode, inout.img_inout(), threshold=self.confidence, pattern=self.pattern)

    def run(self, inout: GpInOut) -> GpInOut:
        inout.rect = self.rect
        # data = oc_gp.ocr(self.mode, img_inout, threshold=self.confidence, pattern=self.pattern)
        # gp_inout.data = data

        inout.data = None
        threading.Thread(target=self.thread_run, args=(inout,)).start()
        while inout.data is None:
            time.sleep(0.01)

        return inout

    def paddleocr_v3(self):
        return self.run(self.gp).data


class CodeScanner(GP):
    name = "条码识别"
    ui_path = "/static/gp/codescanner/"

    def __init__(self, rect: tuple = None, image: Image = None, image_file: str = None):
        self.rect = rect
        self.image = image
        self.image_file = image_file
        self.gp = GpInOut(image=image, image_file=image_file)

    def run(self, gp_inout: GpInOut) -> GpInOut:
        image = gp_inout.image
        if gp_inout.image_file:
            if gp_inout.image_file.startswith("http:"):
                image = capture()
            else:
                image = image_read(gp_inout.image_file)

        offset_x = 0
        offset_y = 0
        if self.rect:
            image = image.crop(self.rect)
            offset_x = self.rect[0]
            offset_y = self.rect[1]

        data = oc.code_scanner(image, offset_x=offset_x, offset_y=offset_y)

        gp_inout.data = data
        return gp_inout

    def scan(self):
        return self.run(self.gp).data


def gp_list():
    gp_s_list = []
    gp_s_list.append("ascript.ios.screen.FindColors")
    gp_s_list.append("ascript.ios.screen.CompareColors")
    gp_s_list.append("ascript.ios.screen.CountingColor")
    gp_s_list.append("ascript.ios.screen.FindImages")
    gp_s_list.append("ascript.ios.screen.Ocr")
    gp_s_list.append("ascript.ios.screen.CodeScanner")
    class_list = []
    for gp_s in gp_s_list:
        module_name, class_name = gp_s.rsplit('.', 1)
        module = gp.load_or_reload_module(module_name)
        gp_class = getattr(module, class_name)
        dao = {"name": gp_class.name, "ui_path": gp_class.ui_path, "id": gp_s, "class_name": class_name,
               "type": "图色工具"}
        class_list.append(dao)
    # print(class_list)
    return class_list
