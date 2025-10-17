import json
from PIL import Image


def api_result_error(e: Exception):
    result = {
        "code": -1,
        "msg": str(e),
        "data": None
    }

    return result


def api_result(code: int = 1, msg: str = "success", data=None, mimetype="application/json"):
    result = {
        "code": code,
        "msg": msg,
        "data": data,
    }

    return result


def api_result_json(code: int = 1, msg: str = "success", data=None):
    result = {
        "code": code,
        "msg": msg,
        "data": data
    }

    return json.dumps(result)


def api_result_for_oc(code=200, mimetype="application/json", data=None):
    if data is None:
        data = api_result_json()

    return {
        "code": code,
        "mimetype": mimetype,
        "data": data
    }


class ImgInout:
    def __init__(self, image: Image.Image = None,
                 image_file: str = None, rect=None):
        self.image = image
        self.image_file = image_file
        self.rect = rect




