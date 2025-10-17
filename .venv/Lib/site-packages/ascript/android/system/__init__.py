import json
import os.path
from abc import ABC, abstractmethod

from airscript.system import R as asR
from airscript.system import Device as asDevice
from airscript.system import Clipboard as asClipboard
from airscript.system import Channel as asChannel
from airscript.data import Kv as asKv
from airscript.intent import Intent as asIntent
from airscript.system import Noti
from airscript.system import Control as asControl
from airscript.system import Progress as asProgress


class R:
    name = asR.moudle_name
    context = asR.context()
    package_name = asR.context().getPackageName()
    id = asR.module_id
    version = asR.getVersionCode()

    @staticmethod
    def res(child_path=None):
        if child_path:
            file_path = child_path.lstrip("/")
            file_path = os.path.join(asR.module_path, "res", file_path)
            return file_path
        return os.path.join(asR.module_path, "res")

    @staticmethod
    def img(child_path=None):
        if child_path:
            file_path = child_path.lstrip("/")
            return os.path.join(asR.module_path, "res/img", file_path)
        return os.path.join(asR.module_path, "res/img")

    @staticmethod
    def ui(child_path=None):
        if child_path:
            file_path = child_path.lstrip("/")
            return os.path.join(asR.module_path, "res/ui", file_path)
        return os.path.join(asR.module_path, "res/ui")

    @staticmethod
    def root(child_path=None):
        if child_path:
            file_path = child_path.lstrip("/")
            file_path = os.path.join(asR.module_path, file_path)
            return file_path
        return asR.module_path

    @staticmethod
    def sd(child_path=None):
        if child_path:
            return asR.sd(child_path)
        return asR.sd()

    @staticmethod
    def rel(path: str = __file__, rel_path: str = None):
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        real_path = os.path.join(path, rel_path)
        real_path = os.path.normpath(real_path)

        return real_path

    @staticmethod
    def get_card():
        return asR.getCard()


def exit():
    asR.exit()


def reboot(delay_time: int = 0):
    asR.reboot(delay_time)


def open(name_or_package: str):
    asIntent.run(name_or_package)


def browser(url: str):
    asIntent.browser(url)


def get_foreground_app(active_time: int = 60):
    return asR.getForegroundApp(active_time)


class ShellListener(ABC):
    @abstractmethod
    def commandOutput(self, i: int, s: str):
        pass

    @abstractmethod
    def commandTerminated(self, i: int, s: str):
        pass

    def commandCompleted(self, i: int, i1: int):
        pass


def shell(command: str, callback: ShellListener = None):
    asProgress.shell(command, callback)


def channel(fun):
    asChannel(fun)


class Device:
    @staticmethod
    def id():
        return asDevice.id()

    @staticmethod
    def name():
        return asDevice.name()

    @staticmethod
    def display():
        return asDevice.display()

    @staticmethod
    def status_bar_height():
        return asDevice.getStatusBarHeight()

    @staticmethod
    def brand():
        return asDevice.brand()

    @staticmethod
    def model():
        return asDevice.model()

    @staticmethod
    def sdk():
        return asDevice.sdk()

    @staticmethod
    def version():
        return asDevice.version()

    @staticmethod
    def ip():
        return asDevice.ip()

    @staticmethod
    def current_appinfo():
        return asDevice.currentAppInfo()

    @staticmethod
    def apps():
        return asDevice.apps()

    @staticmethod
    def battery():
        return asDevice.Battery()

    @staticmethod
    def memory():
        return list(asDevice.Memory())

    @staticmethod
    def set_brightness(value: int):
        asDevice.set_brightness(value)


class Clipboard:
    @staticmethod
    def put(msg: str):
        asClipboard.put(msg)

    @staticmethod
    def get():
        return asClipboard.get()


class KeyValue:
    @staticmethod
    def save(key: str, value):
        asKv.save(key, value)

    @staticmethod
    def get(key: str, default_value):
        return asKv.get(key, default_value)

    @staticmethod
    def remove(key: str):
        return asKv.remove(key)


class Notification:
    @staticmethod
    def listen(call):
        Noti.listener(call)


class Control:
    @staticmethod
    def send(params: dict):
        asControl.send(json.dumps(params))
