from typing import List, Iterable

from airscript.node import Selector as asSelector
from airscript.node import Node as asNode


class Node:
    def __init__(self, node=None):
        super().__init__()
        self._node = node
        self.id = node.id
        self.text = node.text
        self.type = node.type
        self.desc = node.desc
        self.hintText = node.hintText
        self.packageName = node.packageName
        self.path = node.path
        self.rect = node.rect
        self.childCount = node.childCount
        self.inputType = node.inputType
        self.maxTextLength = node.maxTextLength
        self.drawingOrder = node.drawingOrder
        self.depth = node.depth
        self.clickable = node.clickable
        self.checkable = node.checkable
        self.checked = node.checked
        self.editable = node.editable
        self.enabled = node.enabled
        self.visible = node.visible
        self.dismissable = node.dismissable
        self.focusable = node.focusable
        self.focused = node.focused
        self.heading = node.heading
        self.longClickable = node.longClickable
        self.center_x = node.center_x
        self.center_y = node.center_y

    def __dict__(self):
        return {
            'id': self.id,
            'text': self.text,
            'type': self.type,
            'desc': self.desc,
            'hintText': self.hintText,
            'packageName': self.packageName,
            'path': self.path,
            'rect': self.rect,
            'childCount': self.childCount,
            'inputType': self.inputType,
            'maxTextLength': self.maxTextLength,
            'drawingOrder': self.drawingOrder,
            'depth': self.depth,
            'clickable': self.clickable,
            'checkable': self.checkable,
            'checked': self.checked,
            'editable': self.editable,
            'enabled': self.enabled,
            'visible': self.visible,
            'dismissable': self.dismissable,
            'focusable': self.focusable,
            'focused': self.focused,
            'longClickable': self.longClickable,
            'center_x': self.center_x,
            'center_y': self.center_y,
        }

    def find(self, selector):
        res = self.find_all(selector)
        if res and len(res) > 0:
            return res[0]
        return None

    def find_all(self, selector):
        nodes = self._node.find_all(selector.sel)
        res = []
        for n in nodes:
            res.append(Node(n))
        return res

    def __change(self, anode):

        if not anode:
            return None

        # print(type(type(anode)))
        if isinstance(anode, Iterable):
            res = []
            for n in anode:
                res.append(Node(n))
            return res
        else:
            return Node(anode)

    def parent(self, *val: float):
        return self.__change(self._node.parent(*val))

    def child(self, *val: float):
        return self.__change(self._node.child(*val))

    def brother(self, *val: float):
        return self.__change(self._node.brother(*val))

    def click(self):
        self._node.click()
        return self

    def long_click(self):
        self._node.long_click()
        return self

    def swipe(self, ore: int = -1):
        self._node.slide(ore)
        return self

    def slide(self, ore: int = -1):
        self._node.slide(ore)
        return self

    def input(self, msg: str = ""):
        self._node.input(msg)
        return self

    def __str__(self):
        return str(self.__dict__())


class Selector:
    def __init__(self, mode: int = 0):
        super().__init__()
        self.sel = asSelector(mode)

    def find(self) -> Node:
        res = self.find_all(1)
        if res and len(res) > 0:
            return res[0]
        return None

    @staticmethod
    def cache(is_cache: bool):
        asSelector.cache(is_cache)

    @staticmethod
    def dump(mode: int = 0):
        return asSelector.dump(mode)

    def find_all(self, num: int = 999999) -> List[Node]:
        nodes = self.sel.find_all()
        res = []
        if nodes:
            for n in nodes:
                res.append(Node(n))

        if len(res) > 0:
            return res

        return None

    def id(self, val: str):
        if val is None:
            return self
        self.sel.id(val)
        return self

    def text(self, val: str):
        if val is None:
            return self
        self.sel.text(val)
        return self

    def type(self, val: str):
        if val is None:
            return self
        self.sel.type(val)
        return self

    def desc(self, val: str):
        if val is None:
            return self
        self.sel.desc(val)
        return self

    def hintText(self, val: str):
        if val is None:
            return self
        self.sel.hintText(val)
        return self

    def packageName(self, val: str):
        if val is None:
            return self
        self.sel.packageName(val)
        return self

    def path(self, val: str):
        if val is None:
            return self
        self.sel.path(val)
        return self

    def childCount(self, *val: int):
        if val is None:
            return self
        self.sel.childCount(*val)
        return self

    def inputType(self, val: int):
        if val is None:
            return self
        self.sel.inputType(val)
        return self

    def drawingOrder(self, val: int):
        if val is None:
            return self
        self.sel.drawingOrder(val)
        return self

    def depth(self, val: int):
        if val is None:
            return self
        self.sel.depth(val)
        return self

    def maxTextLength(self, val: int):
        if val is None:
            return self
        self.sel.maxTextLength(val)
        return self

    def clickable(self, val: bool):
        if val is None:
            return self
        self.sel.clickable(val)
        return self

    def checkable(self, val: bool):
        if val is None:
            return self
        self.sel.checkable(val)
        return self

    def checked(self, val: bool):
        if val is None:
            return self
        self.sel.checked(val)
        return self

    def editable(self, val: bool):
        if val is None:
            return self
        self.sel.editable(val)
        return self

    def enabled(self, val: bool):
        if val is None:
            return self
        self.sel.enabled(val)
        return self

    def dismissable(self, val: bool):
        if val is None:
            return self
        self.sel.dismissable(val)
        return self

    def focusable(self, val: bool):
        if val is None:
            return self
        self.sel.focusable(val)
        return self

    def focused(self, val: bool):
        if val is None:
            return self
        self.sel.focused(val)
        return self

    def visible(self, val: bool):
        if val is None:
            return self
        self.sel.visible(val)
        return self

    def longClickable(self, val: bool):
        if val is None:
            return self
        self.sel.longClickable(val)
        return self

    def parent(self, *val: float):
        if val is None:
            return self
        self.sel.parent(*val)
        return self

    def child(self, *val: float):
        if val is None:
            return self
        self.sel.child(*val)
        return self

    def brother(self, *val: float):
        if val is None:
            return self
        self.sel.brother(*val)
        return self

    def click(self):
        self.sel.click()
        return self

    def long_click(self):
        self.sel.long_click()
        return self

    def swipe(self, ore: int = -1):
        self.sel.slide(ore)
        return self

    def slide(self, ore: int = -1):
        self.sel.slide(ore)
        return self

    def input(self, msg: str = ""):
        self.sel.input(msg)
        return self
