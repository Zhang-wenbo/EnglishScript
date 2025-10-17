import sys

from ascript.ios.developer.api import api_file, utils, api_module, api_node, dao, api_screen, data, api_code, \
    api_2_android, api_tool, api_label
from ascript.ios.system import R
import traceback


def config(path_home):
    # R.home = path_home
    utils.init(path_home)


http_proxy = {
    # file
    "/api/file/get": api_file.api_file_get,
    "/api/file/copy": api_file.api_file_copy,
    "/api/file/get/image": api_file.api_file_get_image,
    "/api/file/save": api_file.api_file_save,
    "/api/file/create": api_file.api_file_create,
    "/api/file/remove": api_file.api_file_remove,
    "/api/file/rename": api_file.api_file_rename,
    "/api/file/image/crop": api_file.api_file_image_crop,
    "/api/files": api_file.api_files,
    "/api/file/export": api_file.api_dir_export_zip,
    # module
    "/api/module/list": api_module.api_module_list,
    "/api/module/rname": api_module.api_module_rname,
    "/api/module/remove": api_module.api_module_remove,
    "/api/module/create": api_module.api_module_create,
    "/api/module/files": api_module.api_module_files,
    "/api/module/export": api_module.api_module_export,
    "/api/module/run": api_module.api_module_run,
    "/api/module/stop": api_module.api_module_stop,
    "/api/module/runline": api_module.api_module_run_line,
    # node
    "/api/node/dump": api_node.api_node_dump,
    "/api/node/dumpconfig": api_node.api_node_dump_config,
    "/api/node/get/dumpconfig": api_node.api_get_node_dump_config,
    "/api/node/attr": api_node.api_node_attr,
    "/api/node/error": api_node.api_node_error,
    "/api/node/package": api_node.api_node_package,
    # code
    "/api/code/smart": api_code.code_smart,
    # screen
    "/api/screen/capture": api_screen.api_screen_capture,
    "/api/screen/capture/list": api_screen.api_screen_capture_list,
    "/api/screen/gplist": api_screen.api_screen_gplist,
    "/api/screen/gp": api_screen.api_screen_gp,
    "/api/screen/size": api_screen.api_screen_size,
    # tools
    "/api/tool/config/get": api_tool.get_config,
    "/api/tool/config/save": api_tool.save_config,
    # label
    "/api/label/add": api_label.label_add,
    "/api/label/get/img/label": api_label.get_img_label,
    "/api/label/get/label/names": api_label.get_label_names,
    "/api/label/export/cnp": api_label.export_cnp,
    "/api/label/export/yolo/zip": api_label.export_yolo_zip,

}

http_proxy_pycharm = {
    "/api/model/create": api_module.api_module_create,
    "/api/model/get": api_module.api_module_files,
    "/api/file/inputstream/get": api_file.api_file_get,
    "/api/model/getlist": api_module.api_module_list,
    "/api/model/rename": api_module.api_module_rname,
    "/api/model/remove": api_module.api_module_remove,
    "/api/model/run": api_module.api_module_run,
    "/api/model/stop": api_module.api_module_stop,
    "/api/file/dir": api_file.api_files,
    "/api/model/exportplug": api_module.api_module_export
}


def on_req(url: str, args={}):
    res = None

    if url in http_proxy:
        return http_proxy[url](args)

    if url in http_proxy_pycharm:
        return http_proxy_pycharm[url](args)

    # api_file
    # try:
    #     if url in http_proxy:
    #         return http_proxy[url](args)
    #
    #     if url in http_proxy_pycharm:
    #         return http_proxy_pycharm[url](args)
    #
    # except Exception as e:
    #     res = dao.api_result_for_oc(-1, data=str(e))
    #     traceback.print_exc()

    return res


# for watch-jm-file

class ImportWatcher(object):
    _loaded = set()

    @classmethod
    def find_module(cls, name, path, target=None):
        # print(name,path,target)
        if name not in cls._loaded:
            data.eout(name, data.line_id)


sys.meta_path.insert(0, ImportWatcher)
