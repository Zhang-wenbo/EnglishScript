import os.path
import shutil
import sys
from urllib.parse import unquote
from PIL import Image
from flask import Flask, render_template
import io
import json
from PyQt5.QtCore import QByteArray, QBuffer
from flask import app, request, Response
from ascript.windows.screen import FindColors, Ocr, FindImages, CompareColors
from ascript.windows.window import Window
from ascript.windows.client import tools
from ascript.windows.client.dao.server_dao import MFile, Result
from gevent import pywsgi
from ascript.windows.client.ui import get_workspace_list

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

template_folder = os.path.join(current_dir, 'assets\\templates')
static_folder = os.path.join(current_dir, 'assets')
print(template_folder, static_folder)
static_url_path = '../../assets'

app = Flask(__name__, template_folder=template_folder,
            static_folder=static_folder)


@app.route("/")
def page_home():
    return render_template("index.html")


@app.route("/hwnd")
def page_hwnd():
    return render_template("hwnd.html")


@app.route("/colors")
def page_colors():
    return render_template("colors.html")


@app.route("/api/tool/hwnd", methods=['POST'])
def api_tool_hwnd():
    sel_dict = request.json
    print(json.dumps(sel_dict))
    nodes = Window.Selector(dict=sel_dict).exec_find()
    return json.dumps([node.to_dict() for node in nodes])


@app.route("/api/tool/capture")
def api_tool_capture():
    hwnd = request.args.get('hwnd')
    if hwnd:
        win = Window(int(hwnd))
        img = win.capture()
        if img:
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            img.save(buffer, "PNG")
            byte_stream = bytes(byte_array)
            return Response(byte_stream, mimetype='image/png')
        else:
            return '无效图像'
    else:

        #  PIL Image
        img = Window.capture()
        byte_strem = io.BytesIO()
        img.save(byte_strem, format='PNG')
        byte_strem = byte_strem.getvalue()

        return Response(byte_strem, mimetype='image/png')


@app.route("/api/tool/capture/list", methods=['GET'])
def api_tool_capture_list():
    try:
        need_capture = request.args.get("capture")
        print(need_capture)
        if need_capture and need_capture == 'true':
            tools.tool_capture_save()
        capture_dir = os.path.join(current_dir, "assets", "tools", "capture")
        all_pic = os.listdir(capture_dir)

        res = Result(0, "")
        tool_capture_list = []
        for f in all_pic:
            tool_capture_list.append(MFile(os.path.join(capture_dir, f)))

        res.set_data([f.to_dict() for f in tool_capture_list])

        res.data.sort(key=lambda x: x['last_modified'], reverse=True)

        return json.dumps(res.to_dict())
    except Exception as e:
        return json.dumps(Result(0, str(e)).to_dict())


@app.route("/api/file/getpicture", methods=['GET'])
def api_tool_file_getimage():
    file_path = request.args.get("path")
    rect_str = request.args.get("rect")
    max_height = request.args.get("max_height")
    max_width = request.args.get("max_width")
    save_path = request.args.get("save")
    save_convert = request.args.get("ysave")
    rect = None

    if rect_str:
        print(rect_str)
        rect = json.loads(rect_str)

    if file_path:
        img = Image.open(file_path)

        if rect:
            img = img.crop([rect['left'], rect['top'], rect['right'], rect['bottom']])

        if max_height or max_width:
            aspect_ratio = img.size[0] / img.size[1]
            if max_width:
                target_width = int(max_width)
                target_height = int(aspect_ratio * target_width)
                img = img.resize((target_width, max_height))
            elif max_height:
                target_height = int(max_height)
                target_width = int(aspect_ratio * max_height)
                img = img.resize((target_width, target_height))

    byte_strem = io.BytesIO()
    img.save(byte_strem, format='PNG')
    byte_strem = byte_strem.getvalue()

    if save_path:
        save_path = unquote(save_path)
        save_path = save_path.replace('\\', '/')

        if os.path.exists(save_path) and save_convert == 'false':
            print('文件已存在')
            return json.dumps(Result(-1, msg='文件已存在').to_dict())
        else:
            parent_dir = os.path.dirname(save_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            img.save(save_path, format='PNG')

    return Response(byte_strem, mimetype='image/png')


@app.route("/api/file/remove", methods=['GET'])
def api_tool_file_remove():
    file_path = request.args.get("path")
    relative_path = request.args.get("relative")
    target_file = file_path

    if relative_path:
        target_file = os.path.join(current_dir, file_path)
    else:
        target_file = unquote(target_file)

    print(target_file)
    if os.path.isdir(target_file):
        shutil.rmtree(target_file)
    else:
        os.remove(target_file)

    return json.dumps(Result().to_dict())


@app.route("/api/fun/findcolors", methods=['POST'])
def api_fun_findcolors():
    sel_dict = request.json
    print(json.dumps(sel_dict))

    points = FindColors(dict_p=sel_dict).exec_find()
    print(points)

    res = Result(0, "")
    res.set_data([p.to_dict() for p in points])

    return json.dumps(res.to_dict())


@app.route("/api/fun/comparecolors", methods=['POST'])
def api_fun_comparecolors():
    sel_dict = request.json
    print(json.dumps(sel_dict))

    is_equ = CompareColors(dict_p=sel_dict).compare()
    print(is_equ)

    res = Result(0, "")

    res.set_data(is_equ)

    return json.dumps(res.to_dict())


@app.route("/api/fun/findimages", methods=['POST'])
def api_fun_findimages():
    sel_dict = request.json
    print(json.dumps(sel_dict))

    find_imgs = FindImages(dict_p=sel_dict)
    points = None

    if 'findtype' in sel_dict:
        if sel_dict['findtype'] == 'find':
            points = [find_imgs.find()]

        if sel_dict['findtype'] == 'find_all':
            points = find_imgs.find_all(0)

        if sel_dict['findtype'] == 'find_template':
            points = [find_imgs.find_template()]

        if sel_dict['findtype'] == 'find_all_template':
            points = find_imgs.find_all_template()

        if sel_dict['findtype'] == 'find_sift':
            points = [find_imgs.find_sift()]

        if sel_dict['findtype'] == 'find_all_sift':
            points = find_imgs.find_all_sift()

    res = Result(0, "")

    print(points)
    res.set_data(points)

    return json.dumps(res.to_dict())


@app.route("/api/fun/ocr", methods=['POST'])
def api_fun_ocr():
    sel_dict = request.json
    print(json.dumps(sel_dict))

    points = Ocr(dict_p=sel_dict).exec_find_paddle()

    res = Result(0, "")
    if points:
        res.set_data([p.to_dict() for p in points])

    return json.dumps(res.to_dict())


@app.route("/api/model/list", methods=['POST'])
def api_model_list():
    app_list = get_workspace_list()
    file_list = []

    for app in app_list:
        file_list.append(MFile(app))

    res = Result(0, "")
    res.set_data([p.to_dict() for p in file_list])

    return json.dumps(res.to_dict())


def run():
    server = pywsgi.WSGIServer(('127.0.0.1', 8080), app)
    server.serve_forever()


def close():
    print("close")
