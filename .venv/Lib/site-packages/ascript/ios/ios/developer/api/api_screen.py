import io
import os
import sys
import time
from ascript.ios.developer.api import dao
from ascript.ios.developer.api import utils
from ascript.ios.screen import gp_list
from ascript.ios.screen.gp import loadfrom_json
from ascript.ios.system import client

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))


def api_screen_capture(args):
    image = client.screenshot()

    if "path" in args:
        path = utils.path_home_filter(args["path"])
        print(path, "cun")
        directory = os.path.dirname(path)
        # 如果目录不存在，则创建它
        if not os.path.exists(directory):
            os.makedirs(directory)
        res = image.save(path, format='JPEG')
        print(res, "cun-end")

        return dao.api_result_for_oc(data=dao.api_result_json(data=path))

    byte_arr = io.BytesIO()
    image.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()
    return dao.api_result_for_oc(200, mimetype="image/png", data=byte_arr)


# def api_screen_capture_to_file(args):
#     image = client.screenshot()
#     path = args["path"]
#     image.save(path, format='PNG')
#     return dao.api_result_for_oc(data=dao.api_result_json(data=path))


def api_screen_capture_list(args):
    capture = 'false'
    if 'capture' in args:
        capture = args["capture"]

    if not os.path.exists(utils.screen_shot_dir):
        os.makedirs(utils.screen_shot_dir)

    # print(capture)

    if capture == 'true':
        image = client.screenshot()
        timestamp = time.time()
        screenshot_current = os.path.join(utils.screen_shot_dir, f'{timestamp}.png')
        image.save(screenshot_current, format='PNG')

    # 获取文件夹下的所有文件和文件夹名
    file_items = os.listdir(utils.screen_shot_dir)

    file_items = sorted(file_items,
                        key=lambda x: os.path.getmtime(os.path.join(utils.screen_shot_dir, x)), reverse=True)

    data = []
    # 过滤出文件列表，排除文件夹
    for file in file_items:
        file_img = os.path.join(utils.screen_shot_dir, file)
        if os.path.isfile(file_img):
            img_length = os.path.getsize(file_img)
            img_length_format = img_length
            img_lastModified = os.path.getmtime(file_img)
            data.append({
                'path': file_img,
                'name': os.path.basename(file_img),
                'length': img_length_format,
                'length_format': img_length,
                'lastModified': img_lastModified,
                'lastModified_format': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(img_lastModified))
            })

    return dao.api_result_for_oc(data=dao.api_result_json(data=data))


def api_screen_gplist(args):
    return dao.api_result_for_oc(data=dao.api_result_json(data=gp_list()))


def api_screen_gp(args):
    # print(request.form)
    strack = args['strack']
    image_path = args['image']
    if not os.path.exists(image_path):
        projects_index = image_path.find("/Projects/")
        if projects_index != -1:
            image_path = "~/" + image_path[projects_index + len("/Projects/"):]
        image_path = utils.path_home_filter(image_path)

    gp = args['gp']

    gp_dir = os.path.join(utils.gp_home_dir, gp)
    data = loadfrom_json(strack, image_path, gp, gp_dir)

    return dao.api_result_for_oc(data=dao.api_result_json(data=data))


def api_screen_size(args):
    width, height = client.window_size(node=True)
    return dao.api_result_for_oc(data=dao.api_result_json(data={"width": width, "height": height}))
