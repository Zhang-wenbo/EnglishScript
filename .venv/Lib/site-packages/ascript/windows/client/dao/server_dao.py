import os
from typing import Any
from urllib.parse import quote


class Result:
    def __init__(self, code: int = 0, msg: str = ""):
        self.data = None
        self.code = code
        self.msg = msg

    def set_data(self, data: Any):
        self.data = data

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }


class MFile:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.length = os.path.getsize(path)
        self.last_modified = os.path.getmtime(path)
        self.is_file = os.path.isfile(path)

    def to_dict(self):
        return {
            "path": quote(self.path),
            "name": self.name,
            "length": self.length,
            "last_modified": self.last_modified,
            "is_file": self.is_file
        }


