from typing import Union
from ascript.ios import system
from ascript.ios.developer.api import oc
from ascript.ios.screen.gp import Point

KEY_HOME = "home"
KEY_VOLUMEUP = "volumeup"
KEY_volumedown = "volumedown"
KEY_POWER = "power"
KEY_SNAPSHOT = "snapshot"
KEY_POWER_AND_HOME = "power_plus_home"


def click(x, y: int = 0, duration: float = 20):
    if isinstance(x, Point):
        y = x.y
        x = x.x

    x = int(x / system.client.scale)
    y = int(y / system.client.scale)

    system.client.tap(x, y, duration / 1000)




def double_tap(x: int, y: int):
    x = int(x / system.client.scale)
    y = int(y / system.client.scale)
    system.client.double_tap(x, y)


def slide(x1: int, y1: int, x2: int, y2: int, duration: float = 200):
    x1 = int(x1 / system.client.scale)
    y1 = int(y1 / system.client.scale)
    x2 = int(x2 / system.client.scale)
    y2 = int(y2 / system.client.scale)
    system.client.swipe(x1, y1, x2, y2, duration / 1000)


def touch_and_slide(from_x: int,
                    from_y: int,
                    to_x: int,
                    to_y: int,
                    touch_down_duration: int = 500,
                    touch_move_duration: int = 1000,
                    touch_up_duration: int = 500):
    from_x = int(from_x / system.client.scale)
    from_y = int(from_y / system.client.scale)
    to_x = int(to_x / system.client.scale)
    to_y = int(to_y / system.client.scale)

    system.client.touch_and_swipe(from_x, from_y, to_x, to_y,
                                  touch_down_duration / 1000, touch_move_duration / 1000, touch_up_duration / 1000)


def slide_left():
    system.client.swipe_left()


def slide_up():
    system.client.swipe_up()


def slide_right():
    system.client.swipe_right()


def slide_down():
    system.client.swipe_down()


def input(value):
    keys(value)


def home():
    key_press(KEY_HOME)


def keys(value):
    system.client.send_keys(value)


def key_press(key):
    system.client.press(key)


def key_press_hid(key, duration: float = 20):
    system.client.press_duration(key, duration / 1000)
