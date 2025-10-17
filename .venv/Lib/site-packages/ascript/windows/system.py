import os
import sys
import webbrowser


def open():
    pass


def web_open(url: str):
    webbrowser.open(url)


class R:
    _instance = None

    def __new__(cls, root: str=None):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.root = root
        return cls._instance

    def file(self, child_path: str):
        child_path = child_path.replace('/', '\\')
        print(self.root)
        return os.path.join(self.root, child_path)

    @staticmethod
    def current():
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    @staticmethod
    def exit():
        sys.exit(0)
