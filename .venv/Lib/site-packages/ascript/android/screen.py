import  io
import os.path
import threading
from PIL import Image
from airscript.screen import Screen
from airscript.screen import FindColors as asFindColors
from airscript.screen import FindImages as asFindImages
from airscript.screen import GetColorNum as asGetColorNum
from airscript.screen import yolo_v5 as asyolov5
from airscript.screen import Ocr as asOcr
from airscript.screen import CompareColors as asCompareColors
from airscript.screen import QRcode as asQRcode
from airscript.screen import TessOcr
from .system import  R
import aircv
from aircv.isource import Isource
import numpy as np
import cv2

IMG_ANDROID_BITMAP = 1
IMG_PYTHON_IMAGE = 2

MODE_FIND = 1
MODE_FIND_ALL = 2
MODE_FIND_SIFT = 3
MODE_FIND_SIFT_ALL = 4
MODE_FIND_TEMPLATE = 5
MODE_FIND_TEMPLATE_ALL = 6

def cache(is_cache:bool=False):
    Screen.cache(is_cache)

def capture(x:int=None,y:int=None,x1:int=None,y1:int=None):
    img = None
    if x is None:
        img = Screen.bitmap()
    else:
        img = Screen.bitmap(x,y,x1,y1)

    return img

def bitmap_to_file(path:str,bitmap=None,quality=100):

    if bitmap is None:
        bitmap = capture()
    Screen.toFile(path,bitmap,quality)
def file_to_bitmap(path:str,sampleSize:int=1):
    return Screen.file2Bitmap(path,sampleSize)


def bitmap_base64(bitmap=None):
    if bitmap is None:
        bitmap = capture()
    return Screen.base64(bitmap)

def bitmap_maxside(bitmap=None,max_side_len=9999):
    if bitmap is None:
        bitmap = capture()
    return Screen.maxside(bitmap, max_side_len)
def bitmap_to_pilimage(bitmap=None):
    if bitmap is None:
        bitmap = capture()
    byte_array = Screen.toByte(bitmap)
    image_bytes = io.BytesIO(byte_array)
    img = Image.open(image_bytes)
    return img

def get_color_num(colors:str,rect:list=None,sim:float=0.9):
    getcnum = asGetColorNum(colors)
    if rect:
        getcnum.rect(rect[0], rect[1], rect[2], rect[3])
    getcnum.sim(sim)
    return getcnum.find()


class FindColors:
    @staticmethod
    def find(colors:str,rect:list=None,space:int=5,ori:int=2,diff:float=0.9):
        findc = asFindColors(colors)
        if rect:
            findc.rect(rect[0], rect[1], rect[2], rect[3])

        findc.space(space)
        findc.ori(ori)
        hex_diff = str(hex(int((1 - diff) * 255))[2:]).zfill(2)
        findc.diff("#" + hex_diff + hex_diff + hex_diff)
        return findc.find()

    @staticmethod
    def find_all(colors:str,rect:list=None,space:int=5,ori:int=2,diff:float=0.9):
        findc = asFindColors(colors)
        if rect:
            findc.rect(rect[0], rect[1], rect[2], rect[3])

        findc.space(space)
        findc.ori(ori)
        hex_diff = str(hex(int((1 - diff) * 255))[2:]).zfill(2)
        print(hex_diff)
        findc.diff("#" + hex_diff + hex_diff + hex_diff)
        return findc.find_all()


class FindImages:

    @staticmethod
    def __makedao(part_img:str,rect:list=None,confidence:int=0.1):
        if not os.path.exists(part_img):
            part_img = R.img(part_img)
            if not os.path.exists(part_img):
                raise Exception(f"找不到图片文件:{part_img}")

        findi = asFindImages(part_img)

        if rect:
            findi.rect(rect[0], rect[1], rect[2], rect[3])

        findi.confidence(confidence)
        return findi
    
    @staticmethod
    def _get_image_source(rect:list=None):
        if rect:
           source_img = capture(rect[0],rect[1],rect[2],rect[3])
        else:
            source_img = capture()
        
        source_img = bitmap_to_pilimage(source_img)
        image_source = np.array(source_img)
        return image_source


    @staticmethod
    def find(part_img:str,rect:list=None,confidence:float=0.1):
        res = FindImages.find_template(part_img,rect,confidence)
        if res is None:
            return FindImages.find_sift(part_img,rect,confidence)
        return res

    @staticmethod
    def find_all(part_img:str,rect:list=None,confidence:float=0.1):
        res = FindImages.find_all_template(part_img,rect,confidence)
        if res is None:
            return FindImages.find_all_sift(part_img,rect,confidence)
        return res

    @staticmethod
    def find_sift(part_img:str,rect:list=None,confidence:float=0.1,min_match_count=4):
        image_search = aircv.imread(part_img)

        offx = 0
        offy = 0
        if rect:
            offx = rect[0]
            offy = rect[1]

        dao = Isource(FindImages._get_image_source(rect), offx, offy)
        res = dao.find_sift(image_search,min_match_count,confidence)
        return res

    @staticmethod
    def find_all_sift(part_img:str,rect:list=None,confidence:float=0.1,min_match_count=4,maxcnt=0):
        image_search = aircv.imread(part_img)

        offx = 0
        offy = 0
        if rect:
            offx = rect[0]
            offy = rect[1]

        dao = Isource(FindImages._get_image_source(rect), offx, offy)
        res = dao.find_all_sift(image_search,min_match_count,maxcnt,confidence)
        return res

    @staticmethod
    def find_template(part_img:str,rect:list=None,confidence:float=0.1):
        image_search = aircv.imread(part_img)

        offx = 0
        offy = 0
        if rect:
            offx = rect[0]
            offy = rect[1]

        dao = Isource(FindImages._get_image_source(rect), offx, offy)
        res = dao.find_template(image_search,confidence)
        return res

    @staticmethod
    def find_all_template(part_img:str,rect:list=None,confidence:float=0.1):
        image_search = aircv.imread(part_img)

        offx = 0
        offy = 0
        if rect:
            offx = rect[0]
            offy = rect[1]

        dao = Isource(FindImages._get_image_source(rect),offx,offy)
        res = dao.find_all_template(image_search,confidence)

        return res


class YoLov5:
    
    def __init__(self,model_name:str=None,path:str=None):
        super().__init__()
        if model_name:
            self.yolo = asyolov5(model_name)
        elif path:
            self.yolo = asyolov5(path)

    def find_all(self,rect = None):
        if rect:
            return self.yolo.find_all(rect[0],rect[1],rect[2],rect[3])
        return self.yolo.find_all()

class Ocr:
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


    @staticmethod
    def paddleocr_v2(
            rect: list = None,
            pattern: str = None,
            confidence: int = 0.1,
            max_side_len: int = 1200,
            precision: int = 16,
            bitmap=None,
            file: str = None):
        with Ocr.lock:
            ocr = asOcr()
            ocr.mode(2)

            if rect:
                ocr.rect(rect[0], rect[1], rect[2], rect[3])

            if pattern:
                ocr.pattern(pattern)

            ocr.confidence(confidence)
            ocr.max_side_len(max_side_len)
            ocr.precision(precision)
            if bitmap:
                ocr.bitmap(bitmap)

            if file:
                ocr.file(file)

            return ocr.find_all()

    @staticmethod
    def paddleocr_v3(rect: list = None, pattern: str = None,confidence: int = 0.5, max_side_len: int = 1200, precision: int = 16, bitmap=None,
                     file: str = None):
        with Ocr.lock:
            ocr = asOcr()
            ocr.mode(3)
            if rect:
                ocr.rect(rect[0], rect[1], rect[2], rect[3])
            if pattern:
                ocr.pattern(pattern)

            ocr.confidence(confidence)
            ocr.max_side_len(max_side_len)
            ocr.precision(precision)
            if bitmap:
                ocr.bitmap(bitmap)

            if file:
                ocr.file(file)

            return ocr.find_all()

    @staticmethod
    def tess(data_file=Tess_CHI, rect: list = None,pattern:str=None,split_level=RIL_AUTO,white_list:str=None,black_list:str=None):
        tess_core = TessOcr.getInstance(data_file)
        tess_core.split(split_level)
        if rect:
            tess_core.rect(rect)

        if white_list:
            tess_core.writeList(white_list)

        if black_list:
            tess_core.blackList(black_list)

        if pattern:
            tess_core.pattern(pattern)

        return tess_core.find()


class CompareColors:
    @staticmethod
    def compare(colors:str,diff:float=0.9):
        compare = asCompareColors(colors)
        hex_diff = str(hex(int((1 - diff) * 255))[2:]).zfill(2)
        compare.diff("#" + hex_diff + hex_diff + hex_diff)
        return compare.compare()

    @staticmethod
    def compare_until(colors:str,diff:float=0.9):
        compare = asCompareColors(colors)
        hex_diff = str(hex(int((1 - diff) * 255))[2:]).zfill(2)
        compare.diff("#" + hex_diff + hex_diff + hex_diff)
        compare.until()
        return compare.compare()


class QrCode:
    @staticmethod
    def find(rect:list=None,file:str=None,bitmap=None):
        qr = asQRcode()
        if rect:
            qr.rect(rect[0], rect[1], rect[2], rect[3])
        if file:
            qr.file(file)

        if bitmap:
            qr.bitmap(bitmap)

        return qr.find()
















