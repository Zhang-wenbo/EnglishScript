# coding: utf-8

from __future__ import annotations

import atexit
import base64
import io
import logging
import math
import queue
import subprocess
import sys
import threading
import time
import typing
from functools import cached_property
from urllib.parse import urlencode

from PIL import Image
from ._alert import Alert
from ._base import BaseClient
from ._proto import *
from ._types import *
from .exceptions import *
from ._utils import omit_empty

logger = logging.getLogger(__name__)


class CommonClient(BaseClient):
    def __init__(self, wda_url: str):
        super().__init__(wda_url)
        self.__ui_size = None
        self.__debug = False

    @property
    def debug(self) -> bool:
        return self.__debug

    @debug.setter
    def debug(self, v: bool):
        self.__debug = v

    def app_start(self, bundle_id: str, arguments: typing.List[str] = [], environment: typing.Dict[str, str] = {}):
        self.session_request(POST, "/wda/apps/launch", {
            "bundleId": bundle_id,
            "arguments": arguments,
            "environment": environment,
        })

    def app_terminate(self, bundle_id: str):
        self.session_request(POST, "/wda/apps/terminate", {
            "bundleId": bundle_id
        })

    def app_state(self, bundle_id: str) -> AppState:
        value = self.session_request(POST, "/wda/apps/state", {
            "bundleId": bundle_id
        })["value"]
        return AppState(value)

    def app_current(self) -> AppInfo:
        self.unlock()
        st = self.status()
        if st.session_id is None:
            self.session()
        data = self.request(GET, "/wda/activeAppInfo")
        value = data['value']
        return AppInfo.value_of(value)

    def app_list(self) -> AppList:
        value = self.session_request(GET, "/wda/apps/list")
        print(value)
        return AppList.value_of(value)

    def deactivate(self, duration: float):
        self.session_request(POST, "/wda/deactivateApp", {
            "duration": duration
        })

    @cached_property
    def alert(self) -> Alert:
        return Alert(self)

    def sourcetree(self, max_depth: int = 0) -> SourceTree:
        if max_depth > 0:
            data = self.request(GET, "/source", {
                "maxDepth": max_depth
            })
        else:
            data = self.request(GET, "/source")
        return SourceTree.value_of(data)

    def souce_config(self, excluded_attributes: str = None, other_type_filter: int = 1, timeout: int = 60):
        # otherTypefilter值：1:是不过滤默认, 2: 是过滤掉
        payload = {"otherTypefilter": other_type_filter, "timeout": timeout}
        if excluded_attributes is not None and len(excluded_attributes) > 0:
            payload["excludedAttributes"] = excluded_attributes

        query_string = urlencode(payload)

        print(query_string)

        data = self.request(GET, f"/setUpNodeParams?{query_string}")
        return data

    def get_souce_config(self):
        data = self.request(GET, f"/getUpNodeParams")
        return data['value']

    def source(self, max_depth: int = 0) -> str:

        # print("source")

        if max_depth > 0:
            try:
                print("max", max_depth)
                data = self.request(GET, f"/source?maxDepth={max_depth}")
            except Exception as e:
                print(str(e))
        else:
            data = self.request(GET, "/source?maxDepth=50")

        return data['value']

    def open_url(self, url: str):
        self.session_request(POST, "/url", {
            "url": url
        })

    def set_clipboard(self, content: str, content_type="plaintext"):
        """ only works when WDA app is foreground """
        self.session_request(POST, "/wda/setPasteboard", {
            "content": base64.b64encode(content.encode()).decode(),
            "contentType": content_type
        })

    def get_clipboard(self, content_type="plaintext") -> str:
        data = self.session_request(POST, "/wda/getPasteboard", {
            "contentType": content_type
        })
        return base64.b64decode(data['value']).decode('utf-8')

    def appium_settings(self, kwargs: dict = None) -> dict:
        if kwargs is None:
            return self.session_request(GET, "/appium/settings")["value"]
        payload = {"settings": kwargs}
        return self.session_request(POST, "/appium/settings", payload)["value"]

    def is_locked(self) -> bool:
        return self.request(GET, "/wda/locked")["value"]

    def unlock(self):
        self.request(POST, "/wda/unlock")

    def lock(self):
        self.request(POST, "/wda/lock")

    def homescreen(self):
        self.request(POST, "/wda/homescreen")

    def shutdown(self):
        self.request(GET, "/wda/shutdown")

    def get_orientation(self) -> Orientation:
        value = self.session_request(GET, '/orientation')['value']
        return Orientation(value)

    def window_size(self, node=False) -> typing.Tuple[int, int]:
        """
        Returns:
            UISize
        
        Ref:
            FBElementCommands.m
        """

        if node:
            data = self.session_request(GET, "/window/size")
            return data['value']['width'], data['value']['height']
        else:
            # 代码暂时保留，下面的方法为通过截图获取屏幕大小
            # 这里做了一点速度优化，跟进图像大小获取屏幕尺寸
            orientation = self.get_orientation()
            if self.__ui_size is None:
                # 这里认为screenshot返回的屏幕转向时正确的
                pixel_width, pixel_height = self.screenshot().size
                w, h = pixel_width, pixel_height
                if orientation == Orientation.PORTRAIT:
                    self.__ui_size = (w, h)
                else:
                    self.__ui_size = (h, w)

            if orientation == Orientation.LANDSCAPE:
                return self.__ui_size[::-1]
            else:
                return self.__ui_size

    def send_keys(self, value: str):
        """ input with some text """
        self.session_request(POST, "/wda/keys", {"value": list(value)})

    def _percent2pos(self, x, y, window_size=None):
        if any(isinstance(v, float) for v in [x, y]):
            w, h = window_size or self.window_size()
            x = int(x * w) if isinstance(x, float) else x
            y = int(y * h) if isinstance(y, float) else y
            assert w >= x >= 0
            assert h >= y >= 0
        return (x, y)

    def tap(self, x: int, y: int, dur=0.02):
        try:
            self.session_request(POST, "/wda/tap", {"x": x, "y": y, "duration": dur})
        except RequestError:
            self.session_request(POST, "/wda/tap/0", {"x": x, "y": y, "duration": dur})

    def click(self, x, y, duration: typing.Optional[float] = None):
        """
        Combine tap and tap_hold

        Args:
            x, y: can be float(percent) or int
            duration (optional): tap_hold duration
        """
        # x, y = self._percent2pos(x, y)
        if duration:
            return self.touch_and_hold(x, y, duration)
        return self.touch_and_hold(x, y)

    def double_tap(self, x, y):
        """
        Combine tap and tap_hold

        Args:
            x, y: can be float(percent) or int
            duration (optional): tap_hold duration
        """
        # x, y = self._percent2pos(x, y)

        return self.session_request(POST, "/wda/doubleTap", {"x": x, "y": y})

    def calculate_distance(self, l, t, r, b):
        # 定义两个点
        x1, y1 = l, t
        x2, y2 = r, b

        # 计算距离
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        return distance

    def touch_and_swipe(self, from_x: int,
                        from_y: int,
                        to_x: int,
                        to_y: int,
                        touch_down_duration: int = 1,
                        touch_move_duration: int = 1,
                        touch_up_duration: int = 1):

        speed = self.calculate_distance(from_x, from_y, to_x, to_y) / touch_move_duration

        pyload = {
            "fromX": from_x,
            "fromY": from_y,
            "toX": to_x,
            "toY": to_y,
            "pressDuration": touch_down_duration,
            "velocity": speed,
            "holdDuration": touch_up_duration}

        self.session_request(POST, "/wda/pressAndDragWithVelocity", pyload)

    def touch_and_hold(self, x: int, y: int, duration: float = 0.02):
        """ touch and hold
        
        Ref:
            FBElementCommands.m
        """
        self.session_request(POST, "/wda/touchAndHold", {"x": x, "y": y, "duration": duration})

    def swipe(self,
              from_x: int,
              from_y: int,
              to_x: int,
              to_y: int,
              duration: float = 0.05):
        payload = {
            "fromX": from_x,
            "fromY": from_y,
            "toX": to_x,
            "toY": to_y,
            "duration": duration}
        self.session_request(POST, "/wda/dragfromtoforduration", payload)

    def press(self, name: Keycode):
        payload = {
            "name": name
        }
        self.session_request(POST, "/wda/pressButton", payload)

    def press_duration(self, name: Keycode, duration: float):
        hid_usages = {
            "home": 0x40,
            "volumeup": 0xE9,
            "volumedown": 0xEA,
            "power": 0x30,
            "snapshot": 0x65,
            "power_plus_home": 0x65
        }
        name = name.lower()
        if name not in hid_usages:
            raise ValueError("Invalid name:", name)
        hid_usages = hid_usages[name]
        payload = {
            "page": 0x0C,
            "usage": hid_usages,
            "duration": duration
        }
        return self.session_request(POST, "/wda/performIoHidEvent", payload)

    def touch_perform(self, gestures: list[Gesture]):
        """ perform touch actions

        Ref:
            https://appium.readthedocs.io/en/latest/en/commands/interactions/touch/touch-perform/
        """
        payload = {
            "actions": omit_empty(gestures)
        }
        self.session_request(POST, "/wda/touch/perform", payload)

    def volume_up(self):
        self.press(Keycode.VOLUME_UP)

    def volume_down(self):
        self.press(Keycode.VOLUME_DOWN)

    @cached_property
    def scale(self) -> int:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return value['scale']

    def status_barsize(self) -> StatusBarSize:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return StatusBarSize.value_of(value['statusBarSize'])

    def screenshot(self) -> Image.Image:
        """ take screenshot """
        t1 = time.time()
        # print("screenshot-截图开始", t1)
        value = self.request(GET, "/screenshot")["value"]
        # print("screenshot-截图完毕", time.time()-t1)
        raw_value = base64.b64decode(value)
        # print("screenshot-转码结束", time.time() - t1)
        buf = io.BytesIO(raw_value)
        im = Image.open(buf)
        return im.convert("RGB")

    def battery_info(self) -> BatteryInfo:
        data = self.session_request(GET, "/wda/batteryInfo")["value"]
        return BatteryInfo.value_of(data)

    @property
    def info(self) -> DeviceInfo:
        return self.device_info()

    def device_info(self) -> DeviceInfo:
        data = self.session_request(GET, "/wda/device/info")["value"]
        return DeviceInfo.value_of(data)

    def keyboard_dismiss(self, key_names: typing.List[str] = ["前往", "发送", "Send", "Done", "Return"]):
        """ dismiss keyboard
        相当于通过点击键盘上的按钮来关闭键盘

        Args:
            key_names: list of keys to tap to dismiss keyboard
        """
        self.session_request(POST, "/wda/keyboard/dismiss", {"keyNames": key_names})


class XCUITestRecover(Recover):
    def __init__(self, udid: str):
        self._udid = udid

    def recover(self) -> bool:
        """ launch by tidevice
        
        https://github.com/alibaba/tidevice
        """
        logger.info("WDA is starting using tidevice ...")
        args = [sys.executable, '-m', 'tidevice', '-u', self._udid, 'xctest']
        p = subprocess.Popen(args,
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             start_new_session=True,
                             close_fds=True, encoding="utf-8")

        que = queue.Queue()
        threading.Thread(target=self.drain_process_output, args=(p, que), daemon=True).start()
        try:
            success = que.get(timeout=20)
            return success
        except queue.Empty:
            logger.warning("WDA launch timeout 20s")
            p.kill()
            return False

    def drain_process_output(self, p: subprocess.Popen, msg_queue: queue.Queue):
        deadline = time.time() + 10
        lines = []
        while time.time() < deadline:
            if p.poll() is not None:
                logger.warning("xctest exited, output --.\n %s", "\n".join(lines))  # p.stdout.read())
                msg_queue.put(False)
                return
            line = p.stdout.readline().strip()
            lines.append(line)
            # logger.info("%s", line)
            if "WebDriverAgent start successfully" in line:
                logger.info("WDA started")
                msg_queue.put(True)
                break

        atexit.register(p.terminate)
        while p.stdout.read() != "":
            pass


class AppiumClient(CommonClient):
    """
    wdapy for https://github.com/appium/WebDriverAgent
    """

    def __init__(self, wda_url: str = DEFAULT_WDA_URL):
        super().__init__(wda_url)


# def get_single_device_udid() -> str:
#     devices = list_devices()
#     if len(devices) == 0:
#         raise WDAException("No device connected")
#     if len(devices) > 1:
#         raise WDAException("More than one device connected")
#     return devices[0].serial


# class AppiumUSBClient(AppiumClient):
#     def __init__(self, udid: str = None, port: int = 8100):
#         if udid is None:
#             udid = get_single_device_udid()
#         super().__init__(f"http+usbmux://{udid}:{port}")
#         self.set_recover_handler(XCUITestRecover(udid))


class NanoClient(AppiumClient):
    """
    Repo: https://github.com/nanoscopic/WebDriverAgent

    This repo changes a lot recently and the new version code drop the HTTP API to NNG
    So here use the old commit version
    https://github.com/nanoscopic/WebDriverAgent/tree/d07372d73a4cc4dc0b0d7807271e6d7958e57302
    """

    def tap(self, x: int, y: int):
        """ fast tap """
        self.request(POST, "/wda/tap", {
            "x": x,
            "y": y,
        })

    def fast_swipe(self,
                   from_x: int,
                   from_y: int,
                   to_x: int,
                   to_y: int,
                   duration: float = .5):
        """ fast swipe, this method can not simulate back action by swipe left to right """
        self.request(POST, "/wda/swipe", {
            "x1": from_x,
            "y1": from_y,
            "x2": to_x,
            "y2": to_y,
            "delay": duration})

# class NanoUSBClient(NanoClient):
#     def __init__(self, udid: str = None, port: int = 8100):
#         if udid is None:
#             udid = get_single_device_udid()
#         super().__init__(f"http+usbmux://{udid}:{port}")
#         self.set_recover_handler(XCUITestRecover(udid))
