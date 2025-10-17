import json
import os
import sys
import time

from ascript.ios.developer.api import dao
from ascript.ios.node import Selector, Node
from ascript.ios.system import client

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))


def api_node_dump_config(args):
    ex_attrs = None
    if "ex_attrs" in args:
        ex_attrs = args['ex_attrs']

    other_filter = 1
    if "other_filter" in args:
        other_filter = args['other_filter']

    timeout = 60
    if "timeout" in args:
        timeout = args['timeout']

    data = client.souce_config(ex_attrs, other_filter, timeout)

    return dao.api_result_for_oc(data=dao.api_result_json(data=True))


def api_get_node_dump_config(args):
    data = client.get_souce_config()
    print(data, type(data))
    return dao.api_result_for_oc(data=dao.api_result_json(data=data))


def api_node_dump(args):
    try:
        if 'selector' in args:
            selector = args["selector"]
            return dao.api_result_for_oc(data=dao.api_result_json(data=api_selector(client, selector)))

        depth = 0
        if 'depth' in args and len(args['depth']) > 0:
            depth = int(args['depth'])

        xml_info = client.source(depth)
        return dao.api_result_for_oc(200, mimetype="application/xml", data=xml_info)
    except Exception as e:
        print("错误" + str(e))
        return dao.api_result_for_oc(1, mimetype="application/xml", data="")


def api_node_package(args):
    info = client.app_current()
    dict_info = {
        "name": info.name,
        "bundle_id": info.bundle_id,
        "pid": info.pid
    }
    return dao.api_result_for_oc(data=dao.api_result_json(data=dict_info))


def api_node_attr(args):
    node_id = args["node_id"]
    return dao.api_result_for_oc(data=dao.api_result_json(data=element_to_dict(Node(client, node_id))))


def api_node_error(args):
    i = 0 / 0
    return dao.api_result_for_oc(data=dao.api_result_json(data=True))


def api_selector(client, selector: str):
    # print(selector)
    sel = json.loads(selector)

    #    print("?-s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    res = Selector().find_with_dict(client, sel["sel"], sel["find"])
    #    print("?-e", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    return elements_to_dict(res)


def elements_to_dict(element):
    res = []
    nid = 0
    for node in element:
        #        print(node)
        if node:
            res.append({
                "id": node._id,
                # "name": element.name,
                "tag": node._id,
                # "value": element.value,
                # "label": element.label,
                # "displayed": element.displayed,
                # "visible": element.visible,
                # "enabled": element.enabled,
                # "accessible": element.accessible,
                # "x": element.bounds.left,
                # "y": element.bounds.top,
                # "width": element.bounds.right - element.bounds.left,
                # "height": element.bounds.bottom - element.bounds.top,
                "nodeId": nid
            })
        nid = nid + 1

    return res


def element_to_dict(element: Node):
    bounds = element.bounds
    return {
        "id": element.id,
        "type": element.className,
        "tag": element.id,
        "value": element.value,
        "label": element.label,
        "name": element.name,
        "displayed": element.displayed,
        "visible": element.visible,
        "enabled": element.enabled,
        "index": element.index,
        "accessible": element.accessible,
        "x": bounds.left,
        "y": bounds.top,
        "width": bounds.right - bounds.left,
        "height": bounds.bottom - bounds.top,
        "scale": element.scale(),
        "nodeId": 0
    }
