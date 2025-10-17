import json
import os.path
import time
import typing
import requests
from ascript.ios.developer.api import oc, utils, sp_utils
from ascript.ios.wdapy import AppiumClient

# client = AppiumClient()
client = AppiumClient()


class R:

    @staticmethod
    def home():
        return utils.home_dir

    @staticmethod
    def root():
        return utils.r_root

    @staticmethod
    def name():
        return utils.r_name

    def __init__(self):
        pass

    @staticmethod
    def res(child: str = None):
        return os.path.join(R.root(), "res", child)

    @staticmethod
    def img(child: str = None):
        return os.path.join(R.root(), "res", "img", child)

    @staticmethod
    def ui(child: str = None):
        return os.path.join(R.root(), "res", "ui", child)

    @staticmethod
    def rel(path: str = __file__, rel_path: str = None):
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        real_path = os.path.join(path, rel_path)
        real_path = os.path.normpath(real_path)

        return real_path

    @staticmethod
    def assets(file_name: str):
        return os.path.join(utils.assets_space, file_name)


def info():
    return client.info


def get_uuid():
    return oc.getDeviceId()


def get_ios_version():
    return oc.getSystemVersion()


def exit():
    requests.get("http://127.0.0.1:9096/api/module/stop")
    # api_module_stop()


def reboot():
    print("未实现")


def app_start(bundle_id: str, arguments: typing.List[str] = [],
              environment: typing.Dict[str, str] = {}):
    try:
        client.app_start(bundle_id, arguments, environment)
        return True
    except Exception as e:
        print(str(e))
        return False


def scheme_start(scheme: str):
    app_start(oc.get_appBundleID())
    oc.start_scheme(scheme)


def app_stop(bundle_id: str):
    try:
        return client.app_terminate(bundle_id)
    except Exception as e:
        print(str(e))
        return None


def restart_wda(wda_package: str = "com.ascript.webdriveragentrunner.xctrunner"):
    app_start(oc.get_appBundleID())
    app_stop(wda_package)
    scheme_start("aswda://")
    global client
    client = AppiumClient()


def app_state(bundle_id: str):
    try:
        return client.app_state(bundle_id)
    except Exception as e:
        print(str(e))
        return None


def app_current():
    try:
        return client.app_current()
    except Exception as e:
        print(str(e))
        return None


def app_list():
    return client.app_list()


def deactivate(duration: float):
    return client.deactivate(duration)


def open_url(url: str):
    return client.open_url(url)


def is_locked():
    return client.is_locked()


def lock():
    return client.lock()


def unlock():
    return client.unlock()


def set_clipboard(content: str):
    return oc.set_clipboard(content)


def get_clipboard() -> str:
    app_start(oc.get_appBundleID())
    return oc.get_clipboard()


def screen_size():
    return client.window_size()


def screen_orientation():
    return client.get_orientation()


def notify(msg: str, title: str = None, _id: str = "9096"):
    if title is None:
        title = R.name()
    oc.notify(msg=msg, title=title, _id=_id)


class KeyValue:
    @staticmethod
    def save(key: str, value, space=None):
        return oc.save_obj(f"{key}", value)

    @staticmethod
    def get(key: str, default=None, space=None):
        res = oc.get_obj(f"{key}")
        if res is None:
            return default
        return res


class Control:
    last_time = 0

    @staticmethod
    def send(msgs: dict):
        t1 = time.time()
        print("time", t1 - Control.last_time)
        if time.time() - Control.last_time < 0.7:
            print("该函数不能频繁调用")
            return
        if msgs:
            Control.last_time = time.time()
            oc.ws_data(msgs)
