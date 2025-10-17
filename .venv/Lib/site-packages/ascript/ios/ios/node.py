from ascript.ios.wdapy._base import BaseClient
from ascript.ios.wdapy._node import Selector as wda_selector, Element
from ascript.ios import system
from ascript.ios.wdapy import _proto


class _Sel:
    ATTR = 0
    SHIP = 1
    ACTION = 2
    NODE = 4

    def __init__(self, mode: int, key: str, value: object, match: int = -1):
        self.mode = mode
        self.key = key
        self.value = value
        self.match = match

    def _make(self):
        xp = ""
        if self.mode == _Sel.ATTR:
            if self.match == Selector.MODE_CONTAINS:
                xp = f'[contains(@{self.key},"{self.value}")]'
            elif self.match == Selector.MODE_GREATER:
                xp = f'[@{self.key}>"{self.value}"]'
            elif self.match == Selector.MODE_LESS:
                xp = f'[@{self.key}<"{self.value}"]'
            else:
                xp = f'[@{self.key}="{self.value}"]'
        elif self.mode == _Sel.SHIP:
            if self.key == "parent":
                if self.value == 0:
                    xp = "/ancestor::*"
                else:
                    for i in range(self.value):
                        xp = xp + '/..'
            elif self.key == "child":
                print(self.value)
                if self.value == 0:
                    xp = xp + '/*'
                elif self.value < 0:
                    xp = f'/*[last() + {self.value + 1}]'
                elif self.value > 0:
                    xp = f'/*[{self.value}]'
            elif self.key == "brother":
                if self.value == 0:
                    xp = f"/../*"
                elif self.value >= 1:
                    xp = f"/../*[{self.value}]"
                elif self.value <= -1:
                    xp = f"/../*[last() + {self.value + 1}]"
                elif 0 < self.value < 1:
                    formatted_str = "{:.1f}".format(self.value)
                    integer_part, decimal_part = formatted_str.split('.')
                    xp = f"/preceding-sibling::*{decimal_part}"
                    pass
                elif -1 < self.value < 0:
                    formatted_str = "{:.1f}".format(self.value)
                    integer_part, decimal_part = formatted_str.split('.')
                    xp = f"/following-sibling::*{decimal_part}"
                    pass

        # print("xp")

        return xp


class Selector:
    MODE_EQUAL = 0  # 相同
    MODE_CONTAINS = 1
    MODE_MATCHES = 2
    MODE_GREATER = 3  # 大于
    MODE_LESS = 4  # 小于

    MODE_CLICK_ACCESS = 0
    MODE_CLICK_XY = 1

    MODE_SCROLL_VISIBLE = "visible"
    MODE_SCROLL_LEFT = "left"
    MODE_SCROLL_RIGHT = "right"
    MODE_SCROLL_UP = "up"
    MODE_SCROLL_DOWN = "down"

    def __init__(self):
        self.selector = {}
        self.click_action = None
        self.scroll_action = None
        self.set_text_action = None
        self.clear_text_action = None
        self._xpath = None
        self.package_name = None
        self.package_name_match = None
        self.sel = []

    def find_with_dict(self, client, kv: list, max_nums: int = 99999):
        self.selector = {}
        print(kv)
        for sel in kv:
            method = getattr(self, sel['key'], None)
            v = sel["params"]
            if method is not None and callable(method):
                if isinstance(v, list):
                    method(*v)
                else:
                    method(v)

        if max_nums > 1:
            return self.find_all(client)[:max_nums]
        else:
            return [self.find(client)]

    def find(self, client=system.client, timeout: int = 120):
        _proto.DEFAULT_HTTP_TIMEOUT = timeout
        elements = self.find_work(client=client, num=1)
        if elements and len(elements) > 0:
            self.append_action([elements[0]])
            return elements[0]

    def find_all(self, client=system.client, timeout: int = 120):
        _proto.DEFAULT_HTTP_TIMEOUT = timeout
        elements = self.find_work(client)
        self.append_action(elements)
        return elements

    def find_work(self, client=system.client, num: int = -1):

        if self.package_name:
            if self.package_name_match == Selector.MODE_EQUAL:
                if client.app_current().bundle_id != self.package_name:
                    return None
            else:
                if self.package_name not in client.app_current().bundle_id:
                    return None

        if self._xpath:
            return wda_selector(client, xpath=self._xpath).find_all(num=num)

        if len(self.sel) < 1:
            if num == 1:
                return wda_selector(client, xpath="(//*)[1]").find_all(num=num)
            else:
                return wda_selector(client, xpath="//*").find_all(num=num)

        return wda_selector(client, xpath=self._make_xpath()).find_all(num=num)
        # self._make_xpath()
        # return []

    def _make_xpath(self):
        xpath = ""
        for sel in self.sel:
            if xpath == "" and sel.mode == _Sel.ATTR:
                xpath = "//*"
            xpath = xpath + sel._make()
        # print("xpath组合:", xpath)
        return xpath

    def append_action(self, elements):
        for element in elements:
            # print(self.click_action,type(self.click_action), Selector.MODE_CLICK_ACCESS, Selector.MODE_CLICK_XY)
            if self.click_action == Selector.MODE_CLICK_XY:
                element.tap()
            elif self.click_action == Selector.MODE_CLICK_ACCESS:
                element.tap()

            if self.scroll_action:
                # print(self.scroll_action)
                element.scroll(self.scroll_action["mode"], self.scroll_action["distance"])

            if self.clear_text_action:
                element.clear_text()

            if self.set_text_action is not None:
                if self.set_text_action == "":
                    element.clear_text()
                else:
                    element.set_text(self.set_text_action)

    @staticmethod
    def xml():
        return system.client.source()

    def node(self, value, mode=MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.NODE, key="value", value=value, match=mode))
        return self

    def value(self, value, mode=MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="value", value=value, match=mode))
        return self

    def name(self, value: str, mode=MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="name", value=value, match=mode))
        return self

    def label(self, value: str, mode=MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="label", value=value, match=mode))
        return self

    def type(self, value, mode=MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="type", value=value, match=mode))
        return self

    def visible(self, value: bool):
        if value is None:
            return self
        if value:
            p_value = "true"
        else:
            p_value = "false"

        self.sel.append(_Sel(mode=_Sel.ATTR, key="visible", value=p_value))
        return self

    def enabled(self, value: bool):
        if value is None:
            return self
        if value:
            value = "true"
        else:
            value = "false"
        self.sel.append(_Sel(mode=_Sel.ATTR, key="enabled", value=value))
        return self

    def accessible(self, value: bool):
        if value is None:
            return self
        if value:
            value = "true"
        else:
            value = "false"
        self.sel.append(_Sel(mode=_Sel.ATTR, key="accessible", value=value))
        return self

    def index(self, value: int, mode: int = MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="index", value=value, match=mode))
        return self

    def x(self, value: int, mode: int = MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="x", value=value, match=mode))
        return self

    def y(self, value: int, mode: int = MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="y", value=value, match=mode))
        return self

    def width(self, value: int, mode: int = MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="width", value=value, match=mode))
        return self

    def height(self, value: int, mode: int = MODE_EQUAL):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.ATTR, key="height", value=value, match=mode))
        return self

    def child(self, value: float = 0):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.SHIP, key="child", value=value))
        return self

    def parent(self, value: int = 0):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.SHIP, key="parent", value=value))
        return self

    def brother(self, value: float = 0):
        if value is None:
            return self
        self.sel.append(_Sel(mode=_Sel.SHIP, key="brother", value=value))
        return self

    def xpath(self, value: str):
        if value is None:
            return self
        self._xpath = value
        return self

    def predicate(self, value: str):
        self.selector["predicate"] = value
        return self

    def click(self, mode=MODE_CLICK_XY):
        self.click_action = mode
        return self

    def scroll(self, mode=MODE_SCROLL_VISIBLE, distance: float = 1.0):
        self.scroll_action = {"mode": mode, "distance": distance}
        return self

    def input(self, value):
        self.set_text_action = value
        return self

    def clear_text(self, *args):
        self.clear_text_action = 1
        return self

    def package(self, value, mode=MODE_EQUAL):
        self.package_name = value
        self.package_name_match = mode
        return self


class Node(Element):
    # http://127.0.0.1:58817/session/A93BC308-3B79-42D0-B13C-240DA9D3D953/element/BF000000-0000-0000-2000-000000000000/attribute/rect
    def __init__(self, session: BaseClient, id: str):
        super().__init__(session, id)
