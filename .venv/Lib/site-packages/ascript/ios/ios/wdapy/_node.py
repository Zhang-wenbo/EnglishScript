import re
import time
from typing import Optional

import retry

from ascript.ios.wdapy import xcui_element_types, RequestMethod
from ascript.ios.wdapy._base import BaseClient
from ascript.ios.wdapy._types import Rect
from ascript.ios.wdapy._wdapy import CommonClient
from ascript.ios.wdapy.exceptions import WDAStaleElementReferenceError, WDAElementNotFoundError, \
    WDAElementNotDisappearError

DEBUG = False


class Selector(object):
    def __init__(self,
                 client: CommonClient,
                 predicate=None,
                 id=None,
                 className=None,
                 type=None,
                 name=None,
                 nameContains=None,
                 nameMatches=None,
                 text=None,
                 textContains=None,
                 textMatches=None,
                 value=None,
                 valueContains=None,
                 label=None,
                 labelContains=None,
                 visible=None,
                 enabled=None,
                 classChain=None,
                 xpath=None,
                 parent_class_chains=[],
                 timeout=10.0,
                 index=0):
        '''
        Args:
            predicate (str): predicate string
            id (str): raw identifier
            className (str): attr of className
            type (str): alias of className
            name (str): attr for name
            nameContains (str): attr of name contains
            nameMatches (str): regex string
            text (str): alias of name
            textContains (str): alias of nameContains
            textMatches (str): alias of nameMatches
            value (str): attr of value, not used in most times
            valueContains (str): attr of value contains
            label (str): attr for label
            labelContains (str): attr for label contains
            visible (bool): is visible
            enabled (bool): is enabled
            classChain (str): string of ios chain query, eg: **/XCUIElementTypeOther[`value BEGINSWITH 'blabla'`]
            xpath (str): xpath string, a little slow, but works fine
            timeout (float): maxium wait element time, default 10.0s
            index (int): index of founded elements

        WDA use two key to find elements "using", "value"
        Examples:
        "using" can be on of
            "partial link text", "link text"
            "name", "id", "accessibility id"
            "class name", "class chain", "xpath", "predicate string"

        predicate string support many keys
            UID,
            accessibilityContainer,
            accessible,
            enabled,
            frame,
            label,
            name,
            rect,
            type,
            value,
            visible,
            wdAccessibilityContainer,
            wdAccessible,
            wdEnabled,
            wdFrame,
            wdLabel,
            wdName,
            wdRect,
            wdType,
            wdUID,
            wdValue,
            wdVisible
        '''
        assert isinstance(client, CommonClient)
        self._client = client
        self._num = -1
        self._predicate = predicate
        self._id = id
        self._class_name = className or type
        self._name = name
        self._name_part = nameContains or textContains
        self._name_regex = nameMatches or textMatches
        self._value = value
        self._value_part = valueContains
        self._label = label
        self._label_part = labelContains
        self._enabled = enabled
        self._visible = visible
        self._index = index

        self._xpath = self._fix_xcui_type(xpath)
        self._class_chain = self._fix_xcui_type(classChain)
        self._timeout = timeout
        # some fixtures
        if self._class_name and not self._class_name.startswith(
                'XCUIElementType'):
            self._class_name = 'XCUIElementType' + self._class_name
        if self._name_regex:
            if not self._name_regex.startswith(
                    '^') and not self._name_regex.startswith('.*'):
                self._name_regex = '.*' + self._name_regex
            if not self._name_regex.endswith(
                    '$') and not self._name_regex.endswith('.*'):
                self._name_regex = self._name_regex + '.*'
        self._parent_class_chains = parent_class_chains

    def _fix_xcui_type(self, s):
        if s is None:
            return
        re_element = '|'.join(xcui_element_types.ELEMENTS)
        return re.sub(r'/(' + re_element + ')', '/XCUIElementType\g<1>', s)

    def _wdasearch(self, using, value):
        """
        Returns:
            element_ids (list(string)): example ['id1', 'id2']

        HTTP example response:
        [
            {"ELEMENT": "E2FF5B2A-DBDF-4E67-9179-91609480D80A"},
            {"ELEMENT": "597B1A1E-70B9-4CBE-ACAD-40943B0A6034"}
        ]
        """
        element_ids = []
        try:
            if self._num == 1:
                for k, v in self._client.session_request(RequestMethod.POST, "/element", {
                    "using": using,
                    "value": value
                })["value"].items():
                    # print(k, v)
                    if k == "ELEMENT":
                        element_ids.append(v)
            else:
                res = self._client.session_request(RequestMethod.POST, "/elements", {
                    "using": using,
                    "value": value
                })['value']
                for e in res:
                    element_ids.append(e['ELEMENT'])
        except Exception as e:
            pass
            # print(e)

        return element_ids

    # @retry.retry(WDAStaleElementReferenceError, tries=2, delay=.5, jitter=.2)
    def find_element_ids(self):
        elems = []
        if self._id:
            return self._wdasearch('id', self._id)
        if self._predicate:
            return self._wdasearch('predicate string', self._predicate)
        if self._xpath:
            # print('xpath', self._xpath)
            return self._wdasearch('xpath', self._xpath)
        if self._class_chain:
            return self._wdasearch('class chain', self._class_chain)

        chain = '**' + ''.join(
            self._parent_class_chains) + self._gen_class_chain()
        if DEBUG:
            print('CHAIN:', chain)
        return self._wdasearch('class chain', chain)

    def find_all(self, num: int = -1):
        self._num = num
        ids = self.find_element_ids()
        nodes = []
        for n_id in ids:
            nodes.append(Element(self._client, n_id))

        # print(ids)
        return nodes

    def _gen_class_chain(self):
        # just return if aleady exists predicate
        if self._predicate:
            return '/XCUIElementTypeAny[`' + self._predicate + '`]'
        qs = []
        if self._name:
            qs.append("name == '%s'" % self._name)
        if self._name_part:
            qs.append("name CONTAINS %r" % self._name_part)
        if self._name_regex:
            qs.append("name MATCHES %r" % self._name_regex)
        if self._label:
            qs.append("label == '%s'" % self._label)
        if self._label_part:
            qs.append("label CONTAINS '%s'" % self._label_part)
        if self._value:
            qs.append("value == '%s'" % self._value)
        if self._value_part:
            qs.append("value CONTAINS '%s'" % self._value_part)
        if self._visible is not None:
            qs.append("visible == %s" % 'true' if self._visible else 'visible == false')
        if self._enabled is not None:
            qs.append("enabled == %s" % 'true' if self._enabled else 'enabled == false')
        predicate = ' AND '.join(qs)
        chain = '/' + (self._class_name or 'XCUIElementTypeAny')
        if predicate:
            chain = chain + '[`' + predicate + '`]'
        if self._index:
            chain = chain + '[%d]' % self._index

        return chain


class Element(object):
    def __init__(self, client: CommonClient, n_id: str):
        """
        base_url eg: http://localhost:8100/session/$SESSION_ID
        """
        self._session = client
        self._id = n_id

    def __repr__(self):
        return '<Node(id="{}")>'.format(self._id)

    def http(self, method, url, data=None):
        return self._session.session_request(method, url, data)

    def _req(self, method, url, data=None):
        return self.http(method, '/element/' + self._id + url, data)

    def _wda_req(self, method, url, data=None):
        return self.http(method, '/wda/element/' + self._id + url, data)

    def _prop(self, key):
        data = self._req(RequestMethod.GET, '/' + key.lstrip('/'))
        return data['value']

    def _wda_prop(self, key):
        ret = self.http(RequestMethod.GET, '/wda/element/%s/%s' % (self._id, key))['value']
        return ret

    @property
    def info(self):
        return {
            "id": self._id,
            "label": self.label,
            "value": self.value,
            "text": self.text,
            "name": self.name,
            "className": self.className,
            "enabled": self.enabled,
            "displayed": self.displayed,
            "visible": self.visible,
            "accessible": self.accessible,
            "accessibilityContainer": self.accessibility_container
        }

    @property
    def id(self):
        return self._id

    @property
    def label(self):
        return self._prop('attribute/label')

    @property
    def className(self):
        return self._prop('attribute/type')

    @property
    def type(self):
        return self._prop('attribute/type')

    @property
    def index(self):
        return self._prop('attribute/index')

    @property
    def text(self):
        return self._prop('text')

    @property
    def name(self):
        return self._prop('attribute/name')

    @property
    def displayed(self):
        return self._prop("displayed")

    @property
    def enabled(self):
        return self._prop('enabled')

    @property
    def accessible(self):
        return self._wda_prop("accessible")

    @property
    def accessibility_container(self):
        return self._wda_prop('accessibilityContainer')

    @property
    def value(self):
        return self._prop('attribute/value')

    @property
    def visible(self):
        return self._prop('attribute/visible')

    @property
    def bounds(self) -> Rect:
        value = self._prop('rect')
        # scale = self._session.scale
        x, y = value['x'], value['y']
        w, h = value['width'], value['height']
        return Rect(x, y, w, h)

    @property
    def rect(self) -> Rect:
        value = self._prop('rect')
        scale = self._session.scale
        x, y = value['x'], value['y']
        w, h = value['width'], value['height']
        return Rect(x * scale, y * scale, w * scale, h * scale)

    # @property
    def scale(self) -> int:
        return self._session.scale

    # operations
    def tap(self):
        return self._req(RequestMethod.POST, '/click')

    def click(self, dur: int = 0.02):
        """
        Get element center position and do click, a little slower
        """
        # Some one reported, invisible element can not click
        # So here, git position and then do tap
        x, y = self.rect.center
        x = int(x / self._session.scale)
        y = int(y / self._session.scale)
        # print(x, y)
        self._session.tap(x, y, dur)
        # return self.tap()
        return self

    def tap_hold(self, duration=1000):
        """
        Tap and hold for a moment

        Args:
            duration (float): seconds of hold time

        [[FBRoute POST:@"/wda/element/:uuid/touchAndHold"] respondWithTarget:self action:@selector(handleTouchAndHold:)],

        """

        duration = duration / 1000

        self._wda_req(RequestMethod.POST, '/touchAndHold', {'duration': duration})
        return self

    def scroll(self, direction='visible', distance=1.0):
        """
        Args:
            direction (str): one of "visible", "up", "down", "left", "right"
            distance (float): swipe distance, only works when direction is not "visible"

        Raises:
            ValueError

        distance=1.0 means, element (width or height) multiply 1.0
        """
        if direction == 'visible':
            self._wda_req(RequestMethod.POST, '/scroll', {'toVisible': True})
        elif direction in ['up', 'down', 'left', 'right']:
            self._wda_req(RequestMethod.POST, '/scroll', {
                'direction': direction,
                'distance': distance
            })
        else:
            raise ValueError("Invalid direction")
        return self

    # TvOS
    # @property
    # def focused(self):
    #
    # def focuse(self):

    def pickerwheel_select(self):
        """ Select by pickerwheel """
        # Ref: https://github.com/appium/WebDriverAgent/blob/e5d46a85fbdb22e401d396cedf0b5a9bbc995084/WebDriverAgentLib/Commands/FBElementCommands.m#L88
        raise NotImplementedError()

    def pinch(self, scale, velocity):
        """
        Args:
            scale (float): scale must > 0
            velocity (float): velocity must be less than zero when scale is less than 1

        Example:
            pinchIn  -> scale:0.5, velocity: -1
            pinchOut -> scale:2.0, velocity: 1
        """
        data = {'scale': scale, 'velocity': velocity}
        return self._wda_req('post', '/pinch', data)

    def set_text(self, value):
        return self._req(RequestMethod.POST, '/value', {'value': value})

    def clear_text(self):
        return self._req(RequestMethod.POST, '/clear')

    # def child(self, **kwargs):
    #     return Selector(self.__base_url, self._id, **kwargs)

    # todo lot of other operations
    # tap_hold

    def selected(self):
        ''' Element has been selected.
        Returns: bool
        '''

        return self._req(RequestMethod.GET, '/selected').value
