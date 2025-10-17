import time

from airscript.ui import Window as asWindow
from airscript.ui.dialog import toast as astoast
from airscript.ui.dialog import alert as asalert
from airscript.ui.dialog import confirm as asconfirm
from airscript.ui.dialog import promat as aspromat
from airscript.ui import Float as asFloat
from airscript.screen import Screen
from . import screen
import numpy as np
import cv2
from PIL import Image

from airscript.system import R as asR

from .system import Device


class WebWindow:
    def __init__(self, html: str, tunnel=None, id: int = None):
        super().__init__()
        self.id = id
        if tunnel:
            self.window = asWindow(html, tunnel)
        else:
            self.window = asWindow(html)

        if id:
            self.window.id(id)

    def mode(self, mode: int = 0):
        self.window.model(mode)

    def type(self, ftype: int = 0):
        self.window.type(ftype)

    def tunner(self, fun):
        self.window.tunner(fun)

    def size(self, width=None, height=None):
        if width:
            self.window.width(width)

        if height:
            self.window.height(height)

    def background(self, color: str):
        self.window.background(color)

    def drag(self, is_drag: bool = False):
        self.window.drag(is_drag)

    def dim_amount(self, dim: float = 0.5):
        self.window.dimAmount(dim)

    def gravity(self, gravity: int = None, offset_x: int = None, offset_y: int = None):
        if gravity:
            self.window.gravity(gravity)
        if offset_x:
            self.window.x(offset_x)

        if offset_y:
            self.window.y(offset_y)

    def show(self):
        self.window.show()

    def close(self):
        self.window.close()

    def call(self, js: str):
        self.window.call(js)


class Dialog:
    @staticmethod
    def toast(msg, dur=3000, gravity=1 | 16, x=0, y=0.2, bg_color: str = None, color: str = None):
        astoast(msg, dur, gravity, x, y, bg_color, color)

    @staticmethod
    def alert(msg: str, submit: str = "确认"):

        _res = []

        def tunner(k, v):
            if k == '__alert':
                _res.append(True)

        asalert(msg, tunner, submit)

        while len(_res) < 1:
            time.sleep(0.5)
        return True

    @staticmethod
    def confirm(msg: str, title: str = None, submit: str = "确认", cancel: str = "取消"):
        win = asconfirm(msg)
        if title:
            win.title(title)

        __res = []

        def tunner(k, v):
            if k == "__confirm":
                if v == "sure":
                    __res.append(True)
                else:
                    __res.append(False)

        win.submit(submit)
        win.cancle(cancel)
        win.show(tunner)

        while len(__res) < 1:
            time.sleep(0.5)

        return __res[0]

    @staticmethod
    def prompt(msg: str = "请输入信息", title: str = None, value: str = None, hint: str = None, submit: str = "确认",
               cancel: str = "取消"):
        win = aspromat(msg)
        if title:
            win.title(title)

        __res = []

        def tunner(k, v):
            if k == "__promat":
                if v == "cancle":
                    __res.append(False)
                else:
                    __res.extend([True, v])

        win.value(value)
        win.hint(hint)
        win.submit(submit)
        win.cancle(cancel)
        win.show(tunner)

        while len(__res) < 1:
            time.sleep(0.5)

        if __res[0]:
            return __res[1]

        return None


class Loger(WebWindow):
    def __init__(self, html: str = asR.aes("ui/dialog/loger.html")):
        super().__init__(html, id=11)

        self.drag(True)
        self.withclose = False
        self.dim_amount(0)
        self.background("#00000000")

        display = Device.display()
        if display.widthPixels > display.heightPixels:
            self.size("50vh", "50vh")
        else:
            self.size("50vw", "50vw")

        self.mode(3)


class FloatWindow:
    @staticmethod
    def hide():
        asFloat.hide()

    @staticmethod
    def show(x: float = -1, y: float = -1, dim: float = 1):
        asFloat.show(dim, x, y)

    @staticmethod
    def add_menu(menu_id: str, menu_ico: str, menu_click_listener, remove_system: bool = False):
        asFloat.addMenu(menu_id, menu_ico, menu_click_listener, remove_system)


class ImageWindow:
    @staticmethod
    def show(file_or_bitmap_or_ndarray):
        print(type(file_or_bitmap_or_ndarray))
        if type(file_or_bitmap_or_ndarray) == str:
            Screen.show_img_file(file_or_bitmap_or_ndarray)
        elif type(file_or_bitmap_or_ndarray) == np.ndarray:
            # file_or_bitmap_or_ndarray = cv2.cvtColor(file_or_bitmap_or_ndarray, cv2.COLOR_BGR2RGB)
            bitmap = screen.cvimage_to_bitmap(file_or_bitmap_or_ndarray)
            Screen.show_img_bitmap(bitmap)
        elif isinstance(file_or_bitmap_or_ndarray, Image.Image):
            np_image = np.array(file_or_bitmap_or_ndarray)
            opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            bitmap = screen.cvimage_to_bitmap(opencv_image)
            Screen.show_img_bitmap(bitmap)
        else:
            Screen.show_img_bitmap(file_or_bitmap_or_ndarray)
