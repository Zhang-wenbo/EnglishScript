import ctypes
import sys
import pyautogui
import win32con
import win32gui
from PIL import ImageGrab, Image, ImageQt
import re

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)


class Window:

    @staticmethod
    def active():
        return Window(win32gui.GetForegroundWindow())

    @staticmethod
    def screen_size():
        return pyautogui.size()

    def __init__(self, hwnd: int, fill_children: bool = True):
        self.qapp = None
        self.children = None
        self.hwnd = hwnd
        self.title = win32gui.GetWindowText(hwnd)
        self.rect = win32gui.GetWindowRect(hwnd)
        self.name = win32gui.GetClassName(hwnd)
        self.width = self.rect[2] - self.rect[0]
        self.height = self.rect[3] - self.rect[1]
        # 是否最小化
        if fill_children:
            self.__fill_childs(hwnd)

    def __fill_childs(self, hwnd: int):
        self.children = []

        def node_enum(hwnd, extra):
            self.children.append(Window(hwnd))

        win32gui.EnumChildWindows(hwnd, node_enum, None)

    def __str__(self):
        return {'hwnd': self.hwnd, 'title': self.title, 'name': self.name, 'rect': self.rect,
                'active': self.is_active()}.__str__()

    def to_dict(self):
        tempchilds = []

        if self.children:
            for cnode in self.children:
                tempchilds.append(cnode.to_dict())

        return {
            'hwnd': self.hwnd,
            'name': self.name,
            'title': self.title,
            'rect': self.rect,
            'children': tempchilds,
            "placement": self.placement(),
            # "is_maximized": self.is_maximized(),
            "is_active": self.is_active()
        }

    def capture(self) -> Image:
        return pyautogui.screenshot()

    def views(self):
        pass

    def is_active(self) -> bool:
        return is_active(self)

    # def has_focus(self):
    #     return win32gui.GetFocus() == self.hwnd

    def placement(self):
        # return ctypes.windll.user32.IsIconic(self.hwnd) != 0
        return win32gui.GetWindowPlacement(self.hwnd)[0]

    def frame(self, x=None, y=None, w=None, h=None):
        frame(self, x, y, w, h)

    def mize_mini(self):
        mize_mini(self)

    def mize_max(self):
        mize_max(self)

    def mize_normal(self):
        mize_normal(self)

    def close(self):
        win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def __base_re(self, pattern, value):
        if not re.match(pattern, value):
            return False

        return True


def find(
        active: bool = True,
        title: str = None,
        name: str = None,
        hwnd: int = None):
    if hwnd:
        return Window(hwnd)

    window_list = find_all(active, title, name)
    if window_list and len(window_list) > 0:
        return window_list[0]

    return None


def find_all(active: bool = None, title: str = None, name: str = None):
    window_list = []

    def tempcall(hwnd, list):
        window_list.append(Window(hwnd, False))

    win32gui.EnumWindows(tempcall, window_list)

    f_window_list = []
    for w in window_list:

        if active is not None:
            if active != w.is_active():
                continue

        if title is not None:
            if not w.__base_re(title, w.title):
                continue

        if name is not None:
            if not w.__base_re(name, w.title):
                continue

        f_window_list.append(w)

    return f_window_list


def frame(win: Window, x=None, y=None, w=None, h=None):
    if x is None:
        x = win.rect[0]

    if y is None:
        y = win.rect[1]

    if w is None:
        w = win.rect[2] - win.rect[0]

    if h is None:
        h = win.rect[3] - win.rect[1]
    win32gui.MoveWindow(win.hwnd, int(x), int(y), int(w), int(h), True)


def is_active(win: Window) -> bool:
    return win32gui.GetForegroundWindow() == win.hwnd


def mize_mini(win: Window):
    win32gui.ShowWindow(win.hwnd, win32con.SW_MINIMIZE)


def mize_max(win: Window):
    win32gui.ShowWindow(win.hwnd, win32con.SW_MAXIMIZE)


def mize_normal(win: Window):
    win32gui.ShowWindow(win.hwnd, win32con.SW_NORMAL)


def close(self):
    win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
