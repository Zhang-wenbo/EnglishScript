from ascript.ios import system
from ascript.ios.developer.api import oc


def get_device_id():
    return system.client.info.uuid


def get_device_name():
    return system.client.info.name


def get_device_model():
    return system.client.info.model


def get_screen_size():
    return system.client.window_size()


def get_screen_scale():
    return system.client.scale


def get_orientation():
    return system.client.get_orientation()


def get_battery_info():
    return system.client.battery_info()


# duration 毫秒单位
# intensity 0~1 强度，小数
def vibrate(duration, intensity=0.5):
    oc.vibrate(duration, intensity)
