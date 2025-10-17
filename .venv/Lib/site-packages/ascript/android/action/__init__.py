from typing import Union, List

try:
    from android.graphics import Point
    from airscript.action import click as asclick
    from airscript.action import Catch as asCatch
    from airscript.action import slide as asslide
    from airscript.action import touch as astouch
    from airscript.action import input as asinput
    from airscript.action import key as askey
    from ..node import Selector
    from airscript.action import gesture as asgesture
    from airscript.action import path as aspath
    from airscript.action import hid as aHid
    from airscript.action import IME as asIME
except Exception as e:
    print(str(e))


def click(x: Union[int, Point], y: int = None, dur: int = 20):
    if x is None:
        raise Exception("click 参数不能为 None")

    if type(x) == float:
        x = int(x)

    if type(y) == float:
        y = int(y)

    if type(x) == int:
        asclick(x, y, dur)
    else:
        asclick(x, dur)


def swipe(x: int, y: int, x1: int, y1: int, dur: int = 20):
    x = int(x)
    y = int(y)
    x1 = int(x1)
    y1 = int(y1)

    return asslide(x, y, x1, y1, dur)


def slide(x: int, y: int, x1: int, y1: int, dur: int = 20):
    x = int(x)
    y = int(y)
    x1 = int(x1)
    y1 = int(y1)

    return asslide(x, y, x1, y1, dur)


def input(msg: str = "", selector=None):
    if selector:
        asinput(msg, selector.sel)
    else:
        asinput(msg)


class Touch:
    @staticmethod
    def down(x, y, dur: int = 20):
        x = int(x)
        y = int(y)
        astouch.down(x, y, dur)

    @staticmethod
    def move(x, y, dur: int = 20):
        x = int(x)
        y = int(y)
        astouch.move(x, y, dur)

    @staticmethod
    def up(x, y, dur: int = 20):
        x = int(x)
        y = int(y)
        astouch.up(x, y, dur)


class Key:
    @staticmethod
    def home():
        askey.home()

    @staticmethod
    def back():
        askey.back()

    @staticmethod
    def notifactions():
        askey.notifactions()

    @staticmethod
    def lockscreen():
        askey.lockscreen()

    @staticmethod
    def screenshot():
        askey.screenshot()

    @staticmethod
    def recents():
        askey.recents()


class Hid:
    @staticmethod
    def click(x: int, y: int, dur: int = 20):
        x = int(x)
        y = int(y)
        aHid.click(x, y, dur)

    @staticmethod
    def swipe(x: int, y: int, x1: int, y1: int, dur: int = 20):
        x = int(x)
        y = int(y)
        x1 = int(x1)
        y1 = int(y1)
        aHid.slide(x, y, x1, y1, dur)

    @staticmethod
    def slide(x: int, y: int, x1: int, y1: int, dur: int = 20):
        x = int(x)
        y = int(y)
        x1 = int(x1)
        y1 = int(y1)
        aHid.slide(x, y, x1, y1, dur)

    @staticmethod
    def key(**keycode):
        aHid.key(keycode)


class Path:
    def __init__(self, start_time: int = 0, duration: int = 20, will_continue: bool = False):
        self.mpath = aspath(start_time, duration, will_continue)

    def quadTo(self, x1, y1, x2, y2):
        self.mpath.quadTo(x1, y1, x2, y2)

    def lineTo(self, x1, y1):
        self.mpath.lineTo(x1, y1)

    def rCubicTo(self, x1, y1, x2, y2, x3, y3):
        self.mpath.rCubicTo(x1, y1, x2, y2, x3, y3)

    def rMoveTo(self, x1, y1):
        self.mpath.rMoveTo(x1, y1)

    def reset(self):
        self.mpath.reset()

    def rewind(self):
        self.mpath.rewind()

    def moveTo(self, x1, y1):
        self.mpath.moveTo(x1, y1)

    def rQuadTo(self, dx1, dy1, dx2, dy2):
        self.mpath.rQuadTo(dx1, dy1, dx2, dy2)

    def addArc(self, left, top, right, bottom, startAngle, sweepAngle):
        self.mpath.addArc(left, top, right, bottom, startAngle, sweepAngle)

    def addCircle(self, x, y, radius, dir):
        self.mpath.addCircle(x, y, radius, dir)

    def addOval(self, left, top, right, bottom, dir):
        self.mpath.addOval(left, top, right, bottom, dir)

    def addRect(self, left, top, right, bottom, dir):
        self.mpath.addRect(left, top, right, bottom, dir)

    def addRoundRect(self, left, top, right, bottom, rx, ry, dir):
        self.mpath.addRoundRect(left, top, right, bottom, rx, ry, dir)

    def arcTo(self, left, top, right, bottom, startAngle, sweepAngle, forceMoveTo):
        self.mpath.arcTo(left, top, right, bottom, startAngle, sweepAngle, forceMoveTo)

    def cubicTo(self, x1, y1, x2, y2, x3, y3):
        self.mpath.cubicTo(x1, y1, x2, y2, x3, y3)

    def setLastPoint(self, dx, dy):
        self.mpath.setLastPoint(dx, dy)

    def close(self):
        self.mpath.close()

    def rLineTo(self, dx, dy):
        self.mpath.rLineTo(dx, dy)


def gesture(paths: List[Path], listener=None):
    py_paths = []
    for p in paths:
        py_paths.append(p.mpath)

    asgesture.perform(py_paths, listener)


def catch_click(msg: str = None, shine: bool = True):
    asc = asCatch()
    asc.shine(shine)
    asc.msg(msg)
    return asc.click()


class Ime:
    @staticmethod
    def is_active():
        return asIME.is_active()

    @staticmethod
    def input(info: str):
        asIME.input(info)

    @staticmethod
    def input_clear():
        asIME.input("")

    @staticmethod
    def keys(keys: Union[int, list], duration: int = 20):
        if type(keys) is int:
            keys = [keys]
        asIME.keys(keys, duration)

    @staticmethod
    def enter():
        Ime.keys(66)
