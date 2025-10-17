import mimetypes

from ascript.ios.developer.api import label_utils, dao
from ascript.ios.developer.api.dao import api_result_for_oc


def label_add(args):
    label = args["label"]
    label_utils.add_label(label)
    return dao.api_result_for_oc(data=dao.api_result_json())


def get_img_label(args):
    label_dir_name = args["name"]
    label_img_name = args["iname"]
    res = label_utils.get_img_lables(label_dir_name, label_img_name)
    return dao.api_result_for_oc(data=dao.api_result_json(data=res))


def get_label_names(args):
    label_dir_name = args["name"]
    res = label_utils.get_label_names(label_dir_name)
    return dao.api_result_for_oc(data=dao.api_result_json(data=res))

    # get_label_names


def export_cnp(args):
    label_dir_name = args["name"]
    file_path = label_utils.export_cnp(label_dir_name)
    # mine_type, _ = mimetypes.guess_type(file_path)
    # if not mine_type:
    #     mine_type = "application/octet-stream"

    return api_result_for_oc(mimetype="application/zip", data=file_path)


def export_yolo_zip(args):
    label_dir_name = args["name"]
    file_path = label_utils.excport_yolo_zip(label_dir_name)
    # mine_type, _ = mimetypes.guess_type(file_path)
    # if not mine_type:
    #     mine_type = "application/octet-stream"

    return api_result_for_oc(mimetype="application/zip", data=file_path)
