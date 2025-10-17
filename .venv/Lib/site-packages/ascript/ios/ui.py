import uuid

from ascript.ios import system
from ascript.ios.developer.api import oc, utils


class WebWindow:

    def __init__(self, ui_path: str, tunner=None):
        self.uid = str(uuid.uuid4())
        self.ui_path = ui_path
        self.tunner = tunner
        utils.ui_instance[self.uid] = self

    def show(self):
        oc.show_webui(uid=self.uid, ui_path=self.ui_path)
        system.app_start(oc.get_appBundleID())

    def call(self, js_fun: str):
        oc.tunner_py_call_jsfun(self.uid, js_fun)

    def close(self):
        oc.close_webui(uid=self.uid)


class FloatWindow:
    @staticmethod
    def hidden():
        oc.hiddenPictureInPicture()

    @staticmethod
    def hide():
        oc.hiddenPictureInPicture()

    @staticmethod
    def show():
        oc.showPictureInPicture()
