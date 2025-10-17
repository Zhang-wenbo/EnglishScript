# coding: utf-8
#
__all__ = ["Recover", "StatusInfo", "AppInfo", "DeviceInfo", "BatteryInfo", "SourceTree",
           "StatusBarSize", "AppList",
           "Gesture", "GestureOption", "GestureAction"]

import abc
import enum
import typing
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional, Union

from ._proto import *
from ._utils import camel_to_snake


def smart_value_of(obj, data: dict):
    for key, val in data.items():
        setattr(obj, key, val)


class Recover(abc.ABC):
    @abc.abstractmethod
    def recover(self) -> bool:
        pass


class _Base:
    def __init__(self):
        # set default value
        for k, _ in typing.get_type_hints(self).items():
            if not hasattr(self, k):
                setattr(self, k, None)

    def __repr__(self):
        attrs = []
        for k, v in self.__dict__.items():
            attrs.append(f"{k}={v!r}")
        return f"<{self.__class__.__name__} " + ", ".join(attrs) + ">"

    @classmethod
    def value_of(cls, data: dict):
        instance = cls()
        for k, v in data.items():
            key = camel_to_snake(k)
            if hasattr(instance, key):
                setattr(instance, key, v)

        return instance


class AppInfo(_Base):
    name: str
    process_arguments: dict
    pid: int
    bundle_id: str


class StatusInfo(_Base):
    ip: str
    session_id: str
    message: str

    @staticmethod
    def value_of(data: dict) -> "StatusInfo":
        info = StatusInfo()
        value = data['value']
        info.session_id = data['sessionId']
        info.ip = value['ios']['ip']
        info.message = value['message']
        return info

class DeviceInfo(_Base):
    time_zone: str
    current_locale: str
    model: str
    uuid: str
    user_interface_idiom: int
    user_interface_style: str
    name: str
    is_simulator: bool


class BatteryInfo(_Base):
    level: float
    state: BatteryState

    @staticmethod
    def value_of(data: dict) -> "BatteryInfo":
        info = BatteryInfo()
        info.level = data['level']
        info.state = BatteryState(data['state'])
        return info


class SourceTree(_Base):
    value: str
    sessionId: str

class StatusBarSize(_Base):
    width: int
    height: int


class AppList(_Base):
    pid: int
    bundle_id: str


@dataclass
class GestureOption:
    element: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    count: Optional[int] = None
    ms: Optional[int] = None # action:wait duration


@dataclass
class Gesture:
    action: Union[str, GestureAction]
    options: Optional[Union[dict, GestureOption]] = None


@dataclass
class Rect(list):
    def __init__(self, x, y, width, height):
        super().__init__([x, y, width, height])
        self.__dict__.update({
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })

    def __str__(self):
        return 'Rect(x={x}, y={y}, width={w}, height={h})'.format(
            x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return str(self)

    @property
    def center(self):
        return namedtuple('Point', ['x', 'y'])(self.x + self.width // 2,
                                               self.y + self.height // 2)

    @property
    def origin(self):
        return namedtuple('Point', ['x', 'y'])(self.x, self.y)

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height
