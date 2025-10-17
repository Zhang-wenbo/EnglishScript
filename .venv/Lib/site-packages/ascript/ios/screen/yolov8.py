import json
import threading
import time
from typing import Union

from PIL.Image import Image

from ascript.ios.developer.api import oc_gp


def load(param_path: str, bin_path: str, nc: int, use_gpu: bool = False):
    free()
    return oc_gp.yolov8_load(param_path, bin_path, nc, use_gpu)


# def detect(img: Union[Image, str] = None, target_size: int = 640, threshold=0.4, nms_threshold=0.5):
#     if img is None:
#         img = "http://127.0.0.1:8100/screenshot"
#
#     res = oc_gp.yolov8_detect(img, target_size, threshold, nms_threshold)
#
#     return res

yolo_res = None


def detect(img: Union[Image, str] = None, target_size: int = 640, threshold=0.4, nms_threshold=0.5):
    if img is None:
        img = "http://127.0.0.1:8100/screenshot"

    global yolo_res
    yolo_res = None

    def thread_detech():
        global yolo_res
        yolo_res = oc_gp.yolov8_detect(img, target_size, threshold, nms_threshold)

    threading.Thread(target=thread_detech).start()

    while yolo_res is None:
        time.sleep(0.01)

    return yolo_res


def free():
    return oc_gp.yolov8_free()
