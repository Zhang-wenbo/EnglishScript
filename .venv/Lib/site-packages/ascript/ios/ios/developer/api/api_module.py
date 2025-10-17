import json
import os
import shutil
import sys
import time
from datetime import datetime
from . import dao, file_utils, line_helper, oc
from .dao import api_result_for_oc
from ascript.ios.developer.api import utils
# from ascript.ios.system import R
import importlib
import threading

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
developer_dir = os.path.dirname(os.path.dirname(__file__))
run_process = None


def api_module_list(args):
    modules = []
    for m in os.listdir(utils.module_space):
        m_path = os.path.join(utils.module_space, m)
        m_mime = os.path.getmtime(m_path)
        m_format_mime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m_mime))
        m_length = file_utils.convert_bytes(file_utils.get_folder_size(m_path))
        ico_path = os.path.join(m_path, "res/img/logo.png")
        if os.path.isdir(m_path):
            m_dir = {
                "name": m,
                "lastModified": m_mime,
                "lastModified_format": m_format_mime,
                "length_format": m_length,
                "ico": ico_path
            }
            modules.append(m_dir)

    return api_result_for_oc(data=dao.api_result_json(data=modules))


def api_module_rname(args):
    src_dir = os.path.join(utils.module_space, args["name"])
    new_dir = os.path.join(utils.module_space, args["rename"])
    os.rename(src_dir, new_dir)
    return dao.api_result_for_oc()


def api_module_remove(args):
    src_dir = os.path.join(utils.module_space, args["name"])
    shutil.rmtree(src_dir)
    return dao.api_result_for_oc()


def api_module_create(args):
    module_name = args["name"]
    module_dir = os.path.join(utils.module_space, args["name"])

    # spec = importlib.util.find_spec(module_name)

    if is_package_installed(module_name):
        return dao.api_result_for_oc(
            data=dao.api_result_json(code=-1, msg="该名称为内部标准库,不可用.\n请换个名称继续创建."))

    # if not importlib.util.find_spec(module_name):
    #     return dao.api_result_for_oc(
    #         dao.api_result_json(code=-1, msg="该名称为内部标准库,不可用.\n请换个名称继续创建."))

    if not os.path.exists(module_dir):
        os.makedirs(module_dir)
    # 创建 目录结构
    _init_file_ = os.path.join(module_dir, "__init__.py")
    with open(_init_file_, "w") as f:
        f.write('# 导入系统资源模\n')
        f.write('from ascript.ios.system import R,device\n')
        f.write('# 导入动作模块\n')
        f.write('from ascript.ios import action\n')
        f.write('# 导入节点检索模块\n')
        f.write('from ascript.ios import node\n')
        f.write('# 导入图色检索模块\n')
        f.write('from ascript.ios import screen\n')
        f.write('\n')
        f.write('print("Hello AS")')

    # 创建 res/ui 和 res/img/ 并拷贝logo
    img_dir = os.path.join(module_dir, "res/img/")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    ui_dir = os.path.join(module_dir, "res/ui/")
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)
    logo_img = os.path.join(img_dir, "logo.png")

    src_img = os.path.join(developer_dir, "assets/templates/static/img/ico/ico_testing.png")
    # print("路径", src_img, logo_img)
    shutil.copy(src_img, logo_img)

    return dao.api_result_for_oc()


def is_package_installed(package_name):
    """
    检查指定的包是否已安装。

    :param package_name: 要检查的包名（字符串）
    :return: 如果包已安装，则返回True；否则返回False。
    """
    try:
        __import__(package_name)
        return True
    except ModuleNotFoundError:
        return False


def api_module_files(args):
    module_dir = os.path.join(utils.module_space, args["name"])
    if not os.path.exists(module_dir):
        return dao.api_result_for_oc(data=dao.api_result_json(code=0,msg="工程不存在"))

    return dao.api_result_for_oc(data=dao.api_result_json(data=file_utils.get_module_files({}, module_dir)))


def api_module_export(args):
    name = args["name"]
    module_dir = os.path.join(utils.module_space, name)

    files = []
    for root, dirs, file_names in os.walk(utils.cache):
        for file_name in file_names:
            if file_name.endswith('.ias'):
                files.append(os.path.join(root, file_name))

    export_path = os.path.join(utils.cache, f"{name}_{len(files)}.ias")
    utils.zip_folder_contents(module_dir, export_path)
    return dao.api_result_for_oc(mimetype="application/zip", data=export_path)


def run_main(**args):
    utils.r_name = args['name']
    utils.r_root = os.path.join(utils.module_space, utils.r_name)
    # R.name = utils.r_name
    # R.root = utils.r_root
    if utils.module_space not in sys.path:
        sys.path.append(utils.module_space)

    module_name = args['name']
    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = importlib.import_module(module_name)


def api_module_stop(args=None):
    for thread in run_threads:
        if thread.is_alive():
            utils.stop_thread(thread)
        else:
            run_threads.remove(thread)

    run_threads.clear()

    for thread in threading.enumerate():
        if thread.ident not in utils.threads and thread.ident != threading.get_ident() and thread not in run_threads:
            if thread.is_alive():
                utils.stop_thread(thread)

    clear_modules()
    clear_ui()
    # 释放缓存
    utils.is_cache = False

    time.sleep(0.5)

    oc.on_run_state_changed(False)

    return dao.api_result_for_oc(data=dao.api_result_json())


def clear_ui():
    for ui in utils.ui_instance.values():
        ui.close()

    utils.ui_instance = {}


def clear_modules():
    list_pre_del = []
    # sys.modules = run_ms

    for name, module in sys.modules.items():
        try:
            # 尝试获取模块的__file__属性
            file_path = module.__file__
            # print(file_path)
            # 对于某些类型的模块（如C扩展），__file__可能是一个被编译后的文件，
            # 你可能想要获取其源代码文件（如果可用的话），但这通常需要额外的逻辑
            # print(f"{name}: {file_path}")
            if file_path.startswith(utils.module_space) or file_path.startswith(utils.module_line):
                # print(name, file_path)
                list_pre_del.append(name)
        except AttributeError:
            # 如果模块没有__file__属性，则打印一条消息
            pass

    # list_pre_del.sort(key=lambda x: len(x))
    # print(list_pre_del)

    for name in list_pre_del:
        del sys.modules[name]


run_threads = []


def api_module_run(args):
    # if len(run_threads) > 0:
    #     print("检测到已有小程序运行,正在尝试停止")
    #     api_module_stop()
    #     time.sleep(0.1)
    # run_module_name[0] = args['name']

    file_name = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "-" + args['name'] + '.txt'
    log_file = os.path.join(utils.log_space, file_name)
    utils.init_logging(log_file)

    # api_module_stop()
    run_thread = threading.Thread(target=run_main, kwargs=args, daemon=True)
    run_thread.start()
    t_args = {"online": False, "args": args}
    run_thread.name = json.dumps(t_args)
    run_threads.append(run_thread)
    oc.on_run_state_changed(True, t_args)

    return dao.api_result_for_oc(data=dao.api_result_json())


def api_module_run_line(args):
    # if len(run_threads) > 0:
    #     print("检测到已有小程序运行,正在尝试停止")
    #     api_module_stop()
    #     time.sleep(0.1)

    # run_module_name[0] = f"line{args['id']}"
    file_name = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "-" + str(args['id']) + '.txt'
    log_file = os.path.join(utils.log_space, file_name)
    utils.init_logging(log_file)
    run_thread = threading.Thread(target=line_helper.run_line, kwargs=args, daemon=True)
    run_thread.start()
    t_args = {"online": True, "args": args}
    run_thread.name = json.dumps(t_args)
    run_threads.append(run_thread)
    oc.on_run_state_changed(True, t_args)


def run_info():
    if len(run_threads) > 0:
        for thread in run_threads:
            if thread.is_alive():
                return thread.name
    return None
