import logging
import zipfile
import inspect
import ctypes
import os
import shutil
import sys
from logging.handlers import RotatingFileHandler
from ascript.ios import system

home_dir, module_space = "", ""
module_line = ""
label_space = ""

label_yolo_space = ""
cache = ""
data_space = ""
log_space = ""
screen_shot_dir = ""
gp_home_dir = ""
threads = []
ui_instance = {}
r_name = ""
r_root = ""
assets_space = ""
is_cache = False
audio_pool = {}


# client = AppiumClient()


def init(path_home):
    global home_dir, module_space, cache, data_space, screen_shot_dir, gp_home_dir, module_line, log_space, label_space,label_yolo_space,assets_space
    home_dir = path_home
    module_space = os.path.join(home_dir, 'modules')
    module_line = os.path.join(home_dir, 'mline')
    data_space = os.path.join(home_dir, 'data')
    assets_space = os.path.join(home_dir, 'assets')
    label_space = os.path.join(home_dir, "label")
    label_yolo_space = os.path.join(home_dir, "label_yolo")
    cache = os.path.join(data_space, "cache")
    screen_shot_dir = os.path.join(data_space, 'screenshot')
    gp_home_dir = os.path.join(data_space, 'gp')
    log_space = os.path.join(data_space, "log")

    if not os.path.exists(screen_shot_dir):
        os.makedirs(screen_shot_dir)

    if not os.path.exists(gp_home_dir):
        os.makedirs(gp_home_dir)
    sys.path.append(gp_home_dir)

    if not os.path.exists(log_space):
        os.makedirs(log_space)

    if not os.path.exists(module_space):
        os.makedirs(module_space)

    if not os.path.exists(label_space):
        os.makedirs(label_space)

    if not os.path.exists(label_yolo_space):
        os.makedirs(label_yolo_space)

    if not os.path.exists(module_line):
        os.makedirs(module_line)

    if not os.path.exists(assets_space):
        os.makedirs(assets_space)

    if not os.path.exists(cache):
        os.makedirs(cache)
    else:
        # 删除文件夹及其内容
        shutil.rmtree(cache, ignore_errors=True)
        # 重新创建文件夹
        os.makedirs(cache, exist_ok=True)


def path_home_filter(path):
    if path.startswith("~/"):
        path = os.path.join(home_dir, path.replace("~/", ""))
    elif path.startswith("/~/"):
        path = os.path.join(home_dir, path.replace("/~/", ""))

    return path


def zip_folder_contents(folder_path, output_zip_path):
    folder_path = os.path.normpath(folder_path)

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 构造文件的完整路径
                file_path = os.path.join(root, file)
                # 计算arcname，即zip文件中文件的相对路径（不包括顶级目录）
                arcname = os.path.relpath(file_path, folder_path)
                # 写入zip文件
                zipf.write(file_path, arcname)


def unzip_file(zip_path, extract_to):
    """
    解压zip文件到指定目录

    :param zip_path: zip文件的路径
    :param extract_to: 解压到的目标目录路径
    """
    # 确保目标目录存在
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

        # 使用zipfile模块打开zip文件
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 解压所有文件到指定目录
        zip_ref.extractall(extract_to)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        pass
        # raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def init_logging(log_file=None):
    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)  # 例如，设置最大1MB，保留5个备份
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # handler.mode = 'a'
    # if handler in logger.handlers:
    #     logger.removeHandler(handler)
    logger.addHandler(handler)


def recode_loger(msg, t):
    if logger:
        if t == 'i':
            logger.info(msg.rstrip())
        else:
            logger.error(msg.rstrip())


def get_device_id():
    return system.client.info.uuid
