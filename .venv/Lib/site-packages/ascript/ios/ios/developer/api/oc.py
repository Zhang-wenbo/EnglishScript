import os.path

import io
import re
import threading
import time

from PIL.Image import Image
from typing import List
# from ascript.ios.developer.api import utils
from rubicon.objc import ObjCClass
import ctypes
from rubicon.objc import api

from ascript.ios.developer.api import utils, sp_utils
from ascript.ios.wdapy import AppiumClient


# temp_img_path = os.path.join(utils.cache, "find_image_temp.jpg")


def find_all_template(image_source: Image, image_search: List[str], threshold=0.5, offset_xy=(0, 0),
                      rgb: bool = False,
                      max_res=0):
    """
            模版匹配
            给一张大图, 再给一组小图. 循环查找所有小图在大图中的位置.并返回结果数组

            :param image_source: 大图 Python 的PIL Image ,通过这个对象可以存储,可以格式化为bytearray,可以格式化成jpeg等.
            :param image_search: 小图列表
            :param threshold: 相似度不得低于这个值
            :param rgb:是否彩色查找? 一般在opencv中,模版匹配都是对图片进行二值化后查找.所以不区分颜色. 但是我们可以分别匹配 rgb 三个通道模版,来达到彩色图查找的目的.
            :param max_res: 匹配的最多结果数量. 如果是1 就是找到1个匹配结果就可以了,如果是0 就是找到所有

            :return [{
                        result:(x,y), #中心点坐标
                        rect:(l,t,r,b), # 图片在大图中的矩形顶点坐标
                        center_x:x, # 中心点坐标x
                        center_y:y, # 中心点坐标y
                        confidence:相似度
                    },...]
    """
    # 将图像转换为字节流
    image_byte_array = io.BytesIO()
    image_source.save(image_byte_array, format='PNG')
    image_byte_array = image_byte_array.getvalue()
    # print("=============image_source=========================")
    # print(image_source)
    # print("=============image_search=========================")
    # print(image_search)
    # 如果实在ios无法转换 字节流 可存储图片后,将地址传递给oc
    # image_source.save(temp_img_path, format='JPEG')

    # print("子图片", image_search)

    ASOpencvUtils = ObjCClass("ASOpencvUtils")

    def convert_byte_array_to_nsdata(byte_array):
        buffer = (ctypes.c_ubyte * len(byte_array))(*byte_array)
        return ObjCClass('NSData').dataWithBytes_length_(buffer, len(byte_array))

    # print("=======processSmallImageLocationInLargeImage======")

    # 大图data
    large_byte_array = image_byte_array
    # 小图数组集合
    smallOCData_arrays = image_search

    largeOCData = convert_byte_array_to_nsdata(large_byte_array)

    result = ASOpencvUtils.processSmallImageLocationInLargeImage_smallByteArray_(largeOCData, smallOCData_arrays)

    """
        (
                {
                confidence = "0.9939208626747131";
                h = 247;
                w = 176;
                x = 908;
                y = 1738;
            },
                {
                confidence = "0.9939208626747131";
                h = 247;
                w = 176;
                x = 908;
                y = 1738;
            }
        )
        """

    # print("=======result======")
    # print('执行结果', result)

    # print(type(result))

    res = []

    for r in result:
        r = api.py_from_ns(r)
        x = r['x'] + offset_xy[0]
        y = r['y'] + offset_xy[1]
        w = r['w']
        h = r['h']
        c = r['confidence']
        center_x = x + w / 2
        center_y = y + h / 2
        if c >= threshold:
            res.append({
                "result": (center_x, center_y),
                "rect": (x, y, x + w, y + h),
                "center_x": center_x,
                "center_y": center_y,
                "confidence": c
            })

    return res

    # pass


def find_sift(image_source: Image, image_search: List[str], threshold=0.5, offset_xy=(0, 0), rgb: bool = False,
              max_res: int = 0):
    """
        sift 全分辨率匹配
        给一张大图, 再给一组小图. 循环查找所有小图在大图中的位置.并返回结果数组

        :param image_source: 大图 Python 的PIL Image ,通过这个对象可以存储,可以格式化为bytearray,可以格式化成jpeg等.
        :param image_search: 小图列表,列表里是小图的路径
        :param threshold: 相似度不得低于这个值
        :param rgb:是否彩色查找? 一般在opencv中,模版匹配都是对图片进行二值化后查找.所以不区分颜色. 但是我们可以分别匹配 rgb 三个通道模版,来达到彩色图查找的目的.
        :param max_res: 匹配的最多结果数量. 如果是1 就是找到1个匹配结果就可以了,如果是0 就是找到所有

        :return [{
                    result:(x,y), #中心点坐标
                    rect:(l,t,r,b), # 图片在大图中的矩形顶点坐标
                    center_x:x, # 中心点坐标x
                    center_y:y, # 中心点坐标y
                    confidence:相似度
                },...]
    """
    # 将图像转换为字节流
    image_byte_array = io.BytesIO()
    image_source.save(image_byte_array, format='PNG')
    image_byte_array = image_byte_array.getvalue()

    ASOpencvUtils = ObjCClass("ASOpencvUtils")

    def convert_byte_array_to_nsdata(byte_array):
        buffer = (ctypes.c_ubyte * len(byte_array))(*byte_array)
        return ObjCClass('NSData').dataWithBytes_length_(buffer, len(byte_array))

    # print("=======findSiftWithImageSource_imageSearch_threshold_rgb_maxcnt_======")

    # 大图data
    large_byte_array = image_byte_array
    # 小图数组集合
    smallOCData_arrays = image_search

    largeOCData = convert_byte_array_to_nsdata(large_byte_array)

    result = ASOpencvUtils.findSiftWithImageSource_imageSearch_threshold_rgb_maxcnt_(largeOCData, smallOCData_arrays,
                                                                                     threshold, rgb, max_res)

    # print("=======result======")
    # print('执行结果', result)

    # print(type(result))

    res = []

    for r in result:
        r = api.py_from_ns(r)
        x = r['x'] + offset_xy[0]
        y = r['y'] + offset_xy[1]
        w = r['w']
        h = r['h']
        c = r['confidence']
        center_x = x + w / 2
        center_y = y + h / 2
        if c >= threshold:
            res.append({
                "result": (center_x, center_y),
                "rect": (x, y, x + w, y + h),
                "center_x": center_x,
                "center_y": center_y,
                "confidence": c
            })

    return res


def on_run_state_changed(statue: bool, args=None):
    if statue:
        # print("程序开启了")
        if args['online']:
            # print("线上程序", args['args']['id'])
            app_id = args['args']['id']
        else:
            # print("本地工程", args['args']['name'])
            # 工程名称
            name = args['args']['name']

    else:
        # print("程序停止了")
        PythonBridge = ObjCClass("PythonBridge")
        PythonBridge.stopProgramRunningFromPython_('')


def on_log(log):
    msg = log['msg']  # 日志信息
    msg_type = log['type']  # i:info e:error
    msg_time = log['time']  # 时间
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.onProgramRunningLogFromPython_type_time_(msg, msg_type, msg_time)


def on_efile(file_path, app_id):
    # print('解密', file_path, app_id)
    ASAESUtils = ObjCClass("ASAESUtils")
    ASAESUtils.eoutF_appId_(file_path, app_id)


def on_ws_started():
    print('ws启动了')


def ocr(mode: int, image_source: Image, threshold=0.2, offset_x=0, offset_y=0, pattern=None):
    image_byte_array = io.BytesIO()
    image_source.save(image_byte_array, format='PNG')
    image_byte_array = image_byte_array.getvalue()

    def convert_byte_array_to_nsdata(byte_array):
        buffer = (ctypes.c_ubyte * len(byte_array))(*byte_array)
        return ObjCClass('NSData').dataWithBytes_length_(buffer, len(byte_array))

    largeOCData = convert_byte_array_to_nsdata(image_byte_array)
    ASPPOcrUtils = ObjCClass("ASPPOcrUtils")
    result = ASPPOcrUtils.ocrUtilsWithPP_(largeOCData)
    print('执行结果', result)

    res = []

    # print(offset_x, offset_y)

    for r in result:
        r = api.py_from_ns(r)
        x = r['x'] + offset_x
        y = r['y'] + offset_y
        w = r['w']
        h = r['h']
        txt = r['txt']
        c = r['confidence']
        center_x = x + w / 2
        center_y = y + h / 2
        match = True
        if pattern:
            if not re.search(pattern, txt):
                match = False

        if c >= threshold and match:
            res.append({
                "result": (center_x, center_y),
                "rect": (x, y, x + w, y + h),
                "center_x": center_x,
                "center_y": center_y,
                "confidence": c,
                "text": txt
            })
    return res


def set_clipboard(content: str):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.setPasteboardContent_(content)


def get_clipboard() -> str:
    PythonBridge = ObjCClass("PythonBridge")
    return PythonBridge.textFromPasteboard()


# web ui 相关

def show_webui(uid: str, ui_path: str):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.showWebui_url_(uid, ui_path)


def is_webui_show(uid: str):
    PythonBridge = ObjCClass("PythonBridge")
    is_show = PythonBridge.isWebUiShow_(uid)

    # print("===========is_webui_show=================")
    # print(f"uid: {uid}; is_show: {is_show}")


def close_webui(uid: str):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.closeWebui_(uid)


def tunner_py_call_jsfun(uid: str, js_fun: str):
    # print("call js _fun", js_fun)
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.tunnerPyCallJsfun_jsFun_(uid, js_fun)


def tunner_js_call_py(uid, key, value):
    # print("===========tunner_js_call_py=================")
    # print(f"uid:{uid}; key:{key}; value:{value};")

    if uid in utils.ui_instance:
        tunner_fun = utils.ui_instance[uid].tunner
        if tunner_fun:
            tunner_fun(key, value)


def js_save_data(uid: str, key: str, value: str):
    print("===========js_save_data=================")
    print(f"uid:{uid}; key:{key}; value:{value};")
    sp_utils.save(key, value)


def js_get_data(uid: str, key: str, value: str):
    print("===========js_get_data=================")
    print(f"uid:{uid}; key:{key}; value:{value};")
    res = sp_utils.get(key, value)
    print("返回结果", res)
    return res


# 错误信息输出控制台
def js_error_info(uid: str, error: str, js_fun: str):
    print("===========js_error_info=================")
    print(f"uid: {uid};\n js_fun: {js_fun};\n error: {error}; ")


def code_scanner(image: Image, offset_x=0, offset_y=0):
    if image:
        image_byte_array = io.BytesIO()
        image.save(image_byte_array, format='PNG')
        image_byte_array = image_byte_array.getvalue()

        def convert_byte_array_to_nsdata(byte_array):
            buffer = (ctypes.c_ubyte * len(byte_array))(*byte_array)
            return ObjCClass('NSData').dataWithBytes_length_(buffer, len(byte_array))

        largeOCData = convert_byte_array_to_nsdata(image_byte_array)
        ASBarcodeScanningUtils = ObjCClass("ASBarcodeScanningUtils")
        result = ASBarcodeScanningUtils.scanImage_(largeOCData)
    else:
        # ASBarcodeScanningUtils = ObjCClass("ASBarcodeScanningUtils")
        # result = ASBarcodeScanningUtils.scanImage()
        return []
    # print('执行结果', result)

    res = []

    for r in result:
        r = api.py_from_ns(r)
        x = r['x'] + offset_x
        y = r['y'] + offset_y
        w = r['w']
        h = r['h']
        txt = r['txt']
        type = r['type']
        format = r['format']
        center_x = x + w / 2
        center_y = y + h / 2

        res.append({
            "result": (center_x, center_y),
            "rect": (x, y, x + w, y + h),
            "center_x": center_x,
            "center_y": center_y,
            "value": txt,
            "type": type,
            "format": format
        })

    # print('执行结果res:', res)
    return res


def start_scheme(scheme: str):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.startScheme_(scheme)


def notify(msg: str, title: str = None, _id: str = "9096"):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.sendNotificationWithTitle_content_notificationId_(title, msg, _id)


def media_audio_play(path: str, volume=-1.):
    PythonBridge = ObjCClass("PythonBridge")
    _id = PythonBridge.playMusic_volume_(path, volume)
    return str(_id)


def media_audio_stop(_id: str):
    PythonBridge = ObjCClass("PythonBridge")
    _id = PythonBridge.mediaVideoStop_(_id)


def media_audio_complete(_id: str):
    # print(f"media_audio_complete:{_id}")
    if _id in utils.audio_pool:
        utils.audio_pool[_id]()


client = AppiumClient()


def oc_click(x, y):
    # print("click----event", x, y)
    x = int(x / client.scale)
    y = int(y / client.scale)
    client.tap(x, y)
    time.sleep(0.5)


def oc_swipe(action: str):
    w, h = client.window_size(True)
    left = w * 0.2
    right = w * 0.8
    top = h * 0.2
    bottom = h * 0.8
    if action == "left":
        client.swipe(int(right), int(h * 0.5), int(left), int(h * 0.5))
    elif action == "right":
        client.swipe(int(left), int(h * 0.5), int(right), int(h * 0.5))
    elif action == "top":
        client.swipe(int(w * 0.5), int(bottom), int(w * 0.5), int(top))
    elif action == "bottom":
        client.swipe(int(w * 0.5), int(top), int(w * 0.5), int(bottom))

    time.sleep(0.5)


def oc_key(key: str):
    if key == "home":
        client.homescreen()


def ws_data(key: dict):
    ASWSClientManager = ObjCClass("ASWSClientManager")
    ASWSClientManager.sendDeviceInfoMsgFormPy_(key)


def input_text(text: str):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.inputText_(text)


def input_clear():
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.inputClear()


def input_return():
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.inputReturn()


def save_pic2photo(address: str):
    PythonBridge = ObjCClass("PythonBridge")
    successDec = PythonBridge.savePic(address)
    return api.py_from_ns(successDec)


def save_video2photo(address: str):
    PythonBridge = ObjCClass("PythonBridge")
    successDec = PythonBridge.saveVideo(address)
    return api.py_from_ns(successDec)


def save_obj(key: str, value):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.saveData_value_(key, value)


def get_obj(key: str):
    PythonBridge = ObjCClass("PythonBridge")
    valueObj = PythonBridge.getData_(key)
    return api.py_from_ns(valueObj)

def get_appBundleID():
    PythonBridge = ObjCClass("PythonBridge")
    valueObj = PythonBridge.appBundleID()
    return api.py_from_ns(valueObj)

# duration 毫秒单位
# intensity 0~1 强度，小数
def vibrate(duration, intensity):
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.vibrate_intensity_(duration, intensity)
    

def hiddenPictureInPicture():
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.hiddenPictureInPicture()
    

def showPictureInPicture():
    PythonBridge = ObjCClass("PythonBridge")
    PythonBridge.showPictureInPicture()
    

def getDeviceId():
    PythonBridge = ObjCClass("PythonBridge")
    valueObj = PythonBridge.getDeviceId()
    return api.py_from_ns(valueObj)

def getSystemVersion():
    PythonBridge = ObjCClass("PythonBridge")
    valueObj = PythonBridge.getSystemVersion()
    return api.py_from_ns(valueObj)
