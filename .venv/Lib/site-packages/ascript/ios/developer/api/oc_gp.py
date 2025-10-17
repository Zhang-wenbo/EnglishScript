import json
import os.path

import io
import re

from PIL.Image import Image
from typing import List, Union
from rubicon.objc import ObjCClass
import ctypes
from rubicon.objc import api
from ascript.ios.developer.api.dao import ImgInout
from ascript.ios.screen.gp import Point


def image_to_ocdata(image):
    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format='PNG')
    image_byte_array = image_byte_array.getvalue()

    def convert_byte_array_to_nsdata(byte_array):
        buffer = (ctypes.c_ubyte * len(byte_array))(*byte_array)
        return ObjCClass('NSData').dataWithBytes_length_(buffer, len(byte_array))

    # 大图data
    large_byte_array = image_byte_array
    largeOCData = convert_byte_array_to_nsdata(large_byte_array)
    return largeOCData


def screen_cache(cache: bool, img_inout: ImgInout):
    PythonBridge = ObjCClass("PythonBridge")
    if cache:
        if img_inout.image_file:
            result = PythonBridge.startPyImgCache_filePath_fileData_(True, img_inout.image_file, None)
            # print(f"result: {result}")
        elif img_inout.image:
            largeOCData = image_to_ocdata(img_inout.image)
            result = PythonBridge.startPyImgCache_filePath_fileData_(True, None, largeOCData)
    else:
        # print("释放缓存")
        result = PythonBridge.startPyImgCache_filePath_fileData_(False, None, None)


def find_all_template(img_inout: ImgInout, image_search: List[str], threshold=0.5, rgb: bool = False, max_res=-1):
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])
    ASOpencvUtils = ObjCClass("ASOpencvUtils")
    if img_inout.image_file:
        result = ASOpencvUtils.processSmallImgLocationInLargeImgFile_smallByteArray_rect_rgb_threshold_maxCount_(
            img_inout.image_file, image_search, rect_params, rgb, threshold, max_res)
    elif img_inout.image:
        largeOCData = image_to_ocdata(img_inout.image)
        result = ASOpencvUtils.processSmallImageLocationInLargeImage_smallByteArray_rect_threshold_maxCount_(
            largeOCData, image_search, rect_params, threshold, max_res)

    else:
        result = ASOpencvUtils.processSmallImgLocationInLargeImgFile_smallByteArray_rect_rgb_threshold_maxCount_(None,
                                                                                                                 image_search,
                                                                                                                 rect_params,
                                                                                                                 rgb,
                                                                                                                 threshold,
                                                                                                                 max_res)
    res = []
    for r in result:
        r = api.py_from_ns(r)
        x = r['x']
        y = r['y']
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


def find_sift(img_inout: ImgInout, image_search: List[str], threshold=0.5, rgb: bool = False,
              max_res: int = 0):
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])

    ASOpencvUtils = ObjCClass("ASOpencvUtils")
    if img_inout.image_file:
        result = ASOpencvUtils.findSiftWithImgFile_imageSearch_threshold_rect_rgb_maxcnt_(img_inout.image_file,
                                                                                          image_search, threshold,
                                                                                          rect_params, rgb, max_res)
    elif img_inout.image:
        largeOCData = image_to_ocdata(img_inout.image)
        result = ASOpencvUtils.findSiftWithImageSource_imageSearch_threshold_rect_rgb_maxcnt_(largeOCData, image_search,
                                                                                              threshold, rect_params,
                                                                                              rgb, max_res)
    else:
        result = ASOpencvUtils.findSiftWithImgFile_imageSearch_threshold_rect_rgb_maxcnt_(None,
                                                                                          image_search, threshold,
                                                                                          rect_params, rgb, max_res)

    res = []
    for r in result:
        r = api.py_from_ns(r)
        x = r['x']
        y = r['y']
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


def ocr(mode: int, img_inout: ImgInout, threshold=0.2, pattern=None):
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])
    ASPPOcrUtils = ObjCClass("ASPPOcrUtils")
    if img_inout.image_file:
        result = ASPPOcrUtils.ocrUtilsWithPPath_rect_(img_inout.image_file, rect_params)
    elif img_inout.image:
        largeOCData = image_to_ocdata(img_inout.image)
        result = ASPPOcrUtils.ocrUtilsWithPP_rect_(largeOCData, rect_params)
    else:
        result = ASPPOcrUtils.ocrUtilsWithPPath_rect_(None, rect_params)

    res = []

    # print(offset_x, offset_y)

    for r in result:
        r = api.py_from_ns(r)
        x = r['x']
        y = r['y']
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


def code_scanner(image: Image, offset_x=0, offset_y=0):
    print('code_scanner参数：', image)
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
    return res


def find_colors(img_inout: ImgInout, colors, space, ori, diff, num):
    """
        colors: 颜色特征 案例 "801,726,#0968A9|850,682,#FFFFFF|893,726,#FFFFFF"
        space: 最终结果颜色点间隔
        ori: 找色方向
        diff: rgb 三个颜色的每个通道最大绝对值色差.
        num: 最大结果数量
    """

    # 范围参数
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])

    diff = (diff[0] << 16) | (diff[1] << 8) | diff[2]
    ASFindColorHelp = ObjCClass("ASFindColorHelp")
    # 图片参数
    if img_inout.image_file:
        result = ASFindColorHelp.findColor_filePath_colors_diff_ori_space_rect_(num, img_inout.image_file, colors, diff,
                                                                                ori, space, rect_params)
    elif img_inout.image:
        largeOCData = image_to_ocdata(img_inout.image)
        result = ASFindColorHelp.findColor_fileData_colors_diff_ori_space_rect_(num, largeOCData, colors, diff, ori,
                                                                                space, rect_params)
    else:
        result = ASFindColorHelp.findColor_filePath_colors_diff_ori_space_rect_(num, None, colors, diff,
                                                                                ori, space, rect_params)

    res = []

    for r in result:
        ri = api.py_from_ns(r)
        del r
        x = ri['x']
        y = ri['y']
        res.append(Point(x, y))

    del result
    return res


def counting_color(img_inout: ImgInout, colors, diff):
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])

    diff = (diff[0] << 16) | (diff[1] << 8) | diff[2]

    result = 0
    ASFindColorHelp = ObjCClass("ASFindColorHelp")
    if img_inout.image_file:
        result = ASFindColorHelp.countingColorWithPath_colors_rect_diff_(img_inout.image_file, colors, rect_params,
                                                                         diff)
    elif img_inout.image:
        largeOCData = image_to_ocdata(img_inout.image)
        result = ASFindColorHelp.countingColorWithData_colors_rect_diff_(largeOCData, colors, rect_params, diff)
    else:
        result = ASFindColorHelp.countingColorWithPath_colors_rect_diff_(None, colors, rect_params,
                                                                         diff)
    return result


def yolov8_load(param_path: str, bin_path: str, nc: int, use_gpu: bool = False):
    ASNcnnUtils = ObjCClass("ASNcnnUtils")
    return ASNcnnUtils.yolov8Load_binPath_nc_useGpu_(param_path, bin_path, nc, use_gpu)


def yolov8_detect(img: Union[Image, str], target_size: int = 640, threshold=0.4, nms_threshold=0.5):
    result = None
    if isinstance(img, Image):
        largeOCData = image_to_ocdata(img)
        ASNcnnUtils = ObjCClass("ASNcnnUtils")
        result = ASNcnnUtils.yolov8DetectData_targetSize_threshold_nmsThreshold_(largeOCData, target_size, threshold,
                                                                                 nms_threshold)
    else:
        ASNcnnUtils = ObjCClass("ASNcnnUtils")
        result = ASNcnnUtils.yolov8DetectPath_targetSize_threshold_nmsThreshold_(img, target_size, threshold,
                                                                                 nms_threshold)
    # print(result, type(result))

    res = api.py_from_ns(result)

    return json.loads(res)


def yolov8_free():
    ASNcnnUtils = ObjCClass("ASNcnnUtils")
    ASNcnnUtils.yolov8Free()
