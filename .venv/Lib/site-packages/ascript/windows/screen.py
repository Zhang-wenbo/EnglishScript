import json
import os.path
import re
import sys
from urllib.parse import unquote
import numpy
import pyautogui
import win32gui
from PIL import ImageGrab, Image

from ascript.windows.daos.screen import Size, Point, OcrRes
from ascript.windows.utils import screen_utils, airclickcv as aircv
import numpy as np
from ascript.windows.system import R
from ascript.windows.window import Window





def size(hwnd: int = None, rect=None) -> Image:
    temp_img = None
    if hwnd != 0 and hwnd is not None:
        psize = pyautogui.size()
        return Size(psize.width, psize.height)
    else:
        win = Window(hwnd)
        return Size(win.width, win.height)


def capture(hwnd: int = None, rect=None) -> Image:
    temp_img = None
    if hwnd != 0 and hwnd is not None:
        temp_rect = win32gui.GetWindowRect(hwnd)
        temp_img = ImageGrab.grab(temp_rect)
    else:
        temp_img = ImageGrab.grab()

    if rect:
        temp_img = temp_img.crop(rect)
    return temp_img


def get_color(x, y):
    img = capture()
    return img.getpixel((x, y))


def find_colors(colors: str = None, rect=[], sim: float = 0.9, ore: int = 2, space: int = 5, file: str = None,res_num:int=1):
    if res_num>1:
        return FindColors(colors, rect, sim, ore, space, file).find()
    else:
        return FindColors(colors, rect, sim, ore, space, file).find_all(res_num)


def compare_colors( colors: str = None, sim: float = 0.9, img_file: str = None):
        return CompareColors(colors,sim,img_file)

def cor(rect=[], pattern: str = None, confidence: float = 0.1, img_file: str = None,res_num:int =0):
    if res_num ==1:
        return Ocr(rect,pattern=pattern,confidence= confidence,img_path= img_file).find()
    else:
        return Ocr(rect, pattern=pattern, confidence=confidence, img_path=img_file).find_all(res_num)

def find_images(img_part: str = None, rect=None, source_file: str = None, confidence: float = 0.1,res_num:int=1):
    findimg = FindImages(img_part= img_part,source_rect=rect,source_file=source_file,confidence=confidence)
    if res_num==1:
        return findimg.find()
    else:
        return findimg.find_all()

def find_images_template(img_part: str = None, source_rect=None, source_file: str = None, confidence: float = 0.1,res_num:int=1, threshold=0.5, rgb=False, bgremove=False):
    findimg = FindImages(img_part= img_part,source_rect=source_rect,source_file=source_file,confidence=confidence)
    if res_num==1:
        return findimg.find_template(threshold= threshold,bgremove=bgremove,rgb=rgb)
    else:
        return findimg.find_all_template(maxcnt=res_num)

def find_images_sift(img_part: str = None, rect=None, source_file: str = None, confidence: float = 0.1,res_num:int=1, min_match_count: int = 4):
    findimg = FindImages(img_part= img_part,source_rect=rect,source_file=source_file,confidence=confidence)
    if res_num==1:
        return findimg.find_sift(min_match_count= min_match_count)
    else:
        return findimg.find_all_sift(min_match_count= min_match_count)

class FindColors:
    def __init__(self, colors: str = None, rect=[], sim: float = 0.9, ore: int = 2, space: int = 5, file: str = None,
                 dict_p: dict = None):
        self.rect = rect
        self.colors = colors
        self.sim = sim
        self.ore = ore
        self.space = space
        self.res_num = 1
        self.file = file

        if dict_p:
            if 'colors' in dict_p:
                self.colors = dict_p['colors']

            if 'rect' in dict_p:
                self.rect = dict_p['rect']

            if 'sim' in dict_p:
                self.sim = float(dict_p['sim'])

            if 'ore' in dict_p:
                self.ore = int(dict_p['ore'])

            if 'space' in dict_p:
                self.space = int(dict_p['space'])

            if 'file' in dict_p:
                self.file = unquote(dict_p['file'])

            if 'res_num' in dict_p:
                self.res_num = int(dict_p['res_num'])

    def find(self):
        self.res_num = 1
        res = self.exec_find()
        if res and len(res) > 0:
            return res[0]
        return None

    def find_all(self, res_num=sys.maxsize):
        self.res_num = res_num
        res = self.exec_find()
        if res or len(res) > 0:
            return res
        return None

    def exec_find(self):
        # 获取截图
        img = None
        if self.file:
            img = Image.open(self.file)
        else:
            img = ImageGrab.grab()

        if self.rect and len(self.rect) == 4:
            img = img.crop(self.rect)

        # 回填 坐标
        ps = screen_utils.find_colors(self.colors, self.sim, self.res_num, self.ore, img, self.space)
        if ps and self.rect and len(self.rect) == 4:
            for i in range(len(ps)):
                ps[i] = Point(ps[i].x + self.rect[0], ps[i].y + self.rect[1])

        return ps


class CompareColors:
    def __init__(self, colors: str = None, sim: float = 0.9, img_file: str = None, dict_p: dict = None):
        self.colors = colors
        self.sim = sim
        self.img_file = img_file
        if dict_p:
            if 'colors' in dict_p:
                self.colors = dict_p['colors']

            if 'sim' in dict_p:
                self.sim = float(dict_p['sim'])

            if 'path' in dict_p:
                self.img_file = unquote(dict_p['path'])

    def compare(self):
        if self.img_file:
            img = Image.open(self.img_file)
        else:
            img = capture()

        return screen_utils.compare_colors(self.colors, self.sim, img)


class Ocr:

    easyOcr = None

    def easyocr_find(rect=[], pattern: str = None, confidence: float = 0.1, img_path: str = None,
                 dict_p: dict = None):

        return None


    def __init__(self, rect=[], pattern: str = None, confidence: float = 0.1, img_path: str = None,
                 dict_p: dict = None):

        self.rect = rect
        self.pattern = pattern
        self.confidence = confidence
        self.img_path = img_path
        # self.ocr = PaddleOCR(ocr_version='PP-OCRv3')

        if dict_p:
            if 'rect' in dict_p:
                self.rect = dict_p['rect']

            if 'pattern' in dict_p:
                self.pattern = dict_p['pattern']

            if 'img_path' in dict_p:
                self.img_path = unquote(dict_p['img_path'])

            if 'confidence' in dict_p:
                self.sim = float(dict_p['confidence'])

            if 'findtype' in dict_p:
                if dict_p['findtype'] == 'find':
                    self.res_num = 1
                else:
                    self.res_num = 0

        # from easyocr import Reader
        #
        # self.ocr = Reader(['en', 'ch_sim'])

        from paddleocr import PaddleOCR
        self.ocr = PaddleOCR()

    def find(self) -> OcrRes:
        self.res_num = 1
        res = self.exec_find_paddle()
        if res:
            return res[0]
        return None

    def find_all(self, res_num: int = 0) -> [OcrRes]:
        self.res_num = res_num
        res = self.exec_find_paddle()
        return res

    def exec_find(self):
        if self.img_path:
            img = Image.open(self.img_path)
        else:
            img = capture(rect=self.rect)

        if self.rect and len(self.rect) == 4:
            img = img.crop(self.rect)

        # res_source = self.ocr.readtext(np.array(img))

        res_source = self.ocr.ocr(np.array(img))

        print(res_source)

        res = []
        if res_source:
            for r in res_source:
                if self.pattern:
                    pattern = re.compile(self.pattern)
                if r[2] >= self.confidence and (self.pattern is None or pattern.match(r[1])):

                    offsetx = 0
                    offsety = 0
                    if self.rect:
                        offsetx = self.rect[0]
                        offsety = self.rect[1]

                    region_position = r[0]
                    region_position = [[int(region_position[0][0]) + offsetx, int(region_position[0][1]) + offsety],
                                       [int(region_position[1][0]) + offsetx, int(region_position[1][1]) + offsety],
                                       [int(region_position[2][0]) + offsetx, int(region_position[2][1]) + offsety],
                                       [int(region_position[3][0]) + offsetx, int(region_position[3][1]) + offsety]]

                    if self.res_num == 0:
                        res.append(OcrRes(text=r[1], confidence=r[2], region_position=region_position))
                    elif len(res) < self.res_num:
                        res.append(OcrRes(text=r[1], confidence=r[2], region_position=region_position))
                    else:
                        return res

        return res

    def exec_find_paddle(self):
        if self.img_path:
            img = Image.open(self.img_path)
        else:
            img = capture(rect=self.rect)

        if self.rect and len(self.rect) == 4:
            img = img.crop(self.rect)

        res_source = self.ocr.ocr(np.array(img))
        res = []
        if res_source and res_source[0]:
            for r in res_source[0]:

                if self.pattern:
                    pattern = re.compile(self.pattern)
                    # [ [[238.0, 12.0], [330.0, 12.0], [330.0, 40.0], [238.0, 40.0]], ('版本控制', 0.9998359680175781)]

                if r[1][1] >= self.confidence and (self.pattern is None or pattern.match(r[1][0])):

                    offsetx = 0
                    offsety = 0
                    if self.rect:
                        offsetx = int(self.rect[0])
                        offsety = int(self.rect[1])

                    region_position = r[0]
                    region_position = [[int(region_position[0][0]) + offsetx, int(region_position[0][1]) + offsety],
                                       [int(region_position[1][0]) + offsetx, int(region_position[1][1]) + offsety],
                                       [int(region_position[2][0]) + offsetx, int(region_position[2][1]) + offsety],
                                       [int(region_position[3][0]) + offsetx, int(region_position[3][1]) + offsety]]

                    if self.res_num == 0:
                        res.append(OcrRes(text=r[1][0], confidence=r[1][1], region_position=region_position))
                    elif len(res) < self.res_num:
                        res.append(OcrRes(text=r[1][0], confidence=r[1][1], region_position=region_position))
                    else:
                        return res

        return res

    def to_dict(self):
        pass


class FindImages:

    def __init__(self, img_part: str = None, source_rect=None, source_file: str = None, confidence: float = 0.1,
                 dict_p: dict = None):

        self.img_part = img_part
        self.source_rect = source_rect
        self.source_file = source_file
        self.confidence = confidence

        if dict_p:
            if 'image' in dict_p:
                self.img_part = dict_p['image']

            if 'screen' in dict_p:
                self.source_file = unquote(dict_p['screen'])

            if 'sim' in dict_p:
                self.confidence = float(dict_p['sim'])
        else:
            if not os.path.exists(self.img_part):
                self.img_part = R().file("res/img/" + img_part)
                if not os.path.exists(self.img_part):
                    raise ValueError('图片路径不存在:' + self.img_part)

        self.source_img = numpy.array(self.__get_source_img())
        self.search_img = numpy.array(Image.open(self.img_part))

        # self.source_img = cv2.imread("D:\\work\\test\\ac_client\\assets\\tools\\capture\\1703126140.png")
        # self.search_img = cv2.imread("D:\\work\\test\\res\\img\\c.png")

    def find(self, various_size=False):

        res = self.find_template()
        if res:
            return res

        res = self.find_sift()

        return res

    def find_all(self, maxcnt: int = 0, various_size=False):
        res = self.find_all_template()
        if res and len(res) > 0:
            return res

        res = self.find_all_sift()
        return res

    def find_sift(self, min_match_count: int = 4):
        res = self.find_all_sift(maxcnt=1)
        if not res:
            return None
        return res[0]

    def find_all_sift(self, min_match_count: int = 4, maxcnt=0):
        res = aircv.find_all_sift(self.source_img, self.search_img, min_match_count, maxcnt)

        f_res = []
        for r in res:
            if r['confidence'] >= self.confidence:
                f_res.append(r)

        return f_res

    # def find_all_sift_gpt(self, min_match_count: int = 4, maxcnt=0):
    #     return aircv.find_all_sift_gpt(self.source_img, self.search_img, min_match_count, maxcnt)

    def find_template(self, threshold=0.5, rgb=False, bgremove=False):
        f_res = self.find_all_template(maxcnt=1, threshold=threshold, rgb=rgb, bgremove=bgremove)
        if f_res and len(f_res) > 0:
            return f_res[0]
        return None

    def find_all_template(self, maxcnt=0, threshold=0.5, rgb=False, bgremove=False):

        res = aircv.find_all_template(self.source_img, self.search_img, threshold, maxcnt, rgb, bgremove)

        f_res = []
        for r in res:
            if r['confidence'] >= self.confidence:
                f_res.append(r)

        return f_res

    def __get_source_img(self):
        temp_img = None
        if self.source_file:
            temp_img = Image.open(self.source_file)
        else:
            temp_img = capture()

        if self.source_rect and self.source_img.size == 4:
            temp_img = temp_img.resize(self.source_rect)

        return temp_img
