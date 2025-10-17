import os

import jedi
from jedi import settings

from ascript.ios.developer.api import dao, utils


def code_smart(args):
    settings.cache_directory = utils.cache
    source = args['source']
    line = None
    column = None

    if 'line' in args and 'column' in args:
        line = int(args['line'])
        column = int(args['column'])

    script = jedi.api.Script(source)
    c_res = []
    d_res = {}

    try:
        completes = script.complete(line, column)
        definitions = script.get_signatures(line, column)
        if len(completes) > 0 and completes[0].name != 'abs':
            c_res = [c.name for c in completes]

        if definitions and len(definitions) > 0:
            # 假设我们找到了一个定义，并且它是一个函数
            # 注意：这里我们假设第一个定义就是我们要找的，实际情况可能更复杂
            definition = definitions[0]
            try:
                d_res["name"] = definition.name
                d_res["params"] = ', '.join([p.description for p in definition.params])
            except AttributeError:
                pass

    except Exception as e:
        pass
        # print(str(e))

    return dao.api_result_for_oc(data=dao.api_result_json(data={"completes": c_res, "definitions": d_res}))
