import json

from airscript.system import Control as asControl


def connect_to_as(user_dev: str):
    asControl.connect(user_dev, 0)


def connect_to_ws(ws_path:str):
    asControl.connect(ws_path, 1)


def send(params: dict):
    asControl.send(json.dumps(params))


def close():
    asControl.close()
