import json
import os

import jedi
from jedi import settings

from ascript.ios.developer.api import dao, utils
from ascript.ios.developer.api.dao import api_result_for_oc, api_result_json
from ascript.ios.system import KeyValue


def save_config(args):
    KeyValue.save("config", json.loads(args["config"]), "sys")

    # print(KeyValue.get('config',"",'sys'))


def get_config(args):
    return api_result_for_oc(data=api_result_json(data=KeyValue.get("config", "", "sys")))
