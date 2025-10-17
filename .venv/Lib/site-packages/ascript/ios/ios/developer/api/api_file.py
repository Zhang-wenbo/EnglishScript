import io
import json
import mimetypes
import os
import shutil
import time
import zipfile

from PIL import Image
from ascript.ios.developer.api import dao, file_utils
from ascript.ios.developer.api.dao import api_result_for_oc, api_result_json
from ascript.ios.developer.api import utils


def api_file_get(args):
    file_path = utils.path_home_filter(args["path"])
    mine_type, _ = mimetypes.guess_type(file_path)
    if not mine_type:
        mine_type = "application/octet-stream"

    return api_result_for_oc(mimetype=mine_type, data=file_path)


def api_file_copy(args: dict = None):
    source_path = args["source"]
    target_path = args["target"]
    source_path = utils.path_home_filter(source_path)
    target_path = utils.path_home_filter(target_path)

    if not os.path.exists(os.path.dirname(target_path)):
        os.makedirs(os.path.dirname(target_path))
    shutil.copy(source_path, target_path)
    return api_result_for_oc()


def api_file_get_image(args):
    file_path = os.path.join(utils.module_space, args["path"])
    file_path = utils.path_home_filter(file_path)
    if not os.path.exists(file_path):
        return api_result_for_oc(404, data={})
    max_height = -1
    if "maxheight" in args:
        max_height = int(args['maxheight'])

    if max_height < 0:
        with Image.open(file_path) as img:
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            byte_arr = byte_arr.getvalue()
            return api_result_for_oc(200, mimetype='image/png', data=byte_arr)
    else:
        with Image.open(file_path) as img:
            width, height = img.size
            target_width = int(width * (max_height / height))
            resized_img = img.resize((target_width, max_height))
            byte_arr = io.BytesIO()
            resized_img.save(byte_arr, format='PNG')
            byte_arr = byte_arr.getvalue()
            return api_result_for_oc(200, mimetype='image/png', data=byte_arr)


def api_file_save(args):
    file_path = utils.path_home_filter(args["path"])
    content = args["content"]
    if not os.path.exists(file_path):
        return "File does not exist", 404

    with open(file_path, "w", newline='\n', encoding="utf-8") as f:
        f.write(content)

    return api_result_for_oc()


def api_file_create(args: dict = None):
    try:
        file_path = utils.path_home_filter(args["path"])
        file_name = args["name"]
        file_type = args["type"]

        new_file = os.path.join(file_path, file_name)

        if os.path.exists(new_file):
            return dao.api_result_for_oc(data=dao.api_result_json(code=0, msg="文件已存在"))

        if file_type == "file":

            if not os.path.exists(os.path.dirname(new_file)):
                os.makedirs(os.path.dirname(new_file))

            with open(new_file, "w") as f:
                pass
        else:
            os.makedirs(new_file)

        # return api_result_for_oc()
        return dao.api_result_for_oc(data=dao.api_result_json())
    except Exception as e:
        return dao.api_result_for_oc(data=dao.api_result_json(code=0, msg=str(e)))


def api_dir_export_zip(args):
    label_root_dir = utils.path_home_filter(args["path"])
    zip_name = args["name"]
    output_zip_path = os.path.join(utils.cache, zip_name)
    # print(output_zip_path)

    """
        将文件夹压缩成ZIP文件

        :param folder_path: 文件夹路径
        :param output_zip_path: 输出的ZIP文件路径
        """
    # 检查文件夹是否存在
    if not os.path.isdir(label_root_dir):
        raise FileNotFoundError(f"The folder {label_root_dir} does not exist.")

    # 创建ZIP文件
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(label_root_dir):
            # 对于根目录下的文件，直接使用文件名作为arcname
            if root == label_root_dir:
                arcname_root = ''
            else:
                # 对于子目录中的文件，使用相对于根目录的路径（去掉根目录名本身）
                arcname_root = os.path.relpath(root, label_root_dir)
                if arcname_root.startswith(os.sep):  # 在Windows上可能是'\'，在Unix/Linux上可能是'/'
                    arcname_root = arcname_root[len(os.sep):]

            for file in files:
                # 创建ZIP文件内的完整路径
                if file.endswith('.cnp'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.join(arcname_root, file)
                # 将文件添加到ZIP文件中
                zipf.write(file_path, arcname)

    return api_result_for_oc(mimetype="application/zip", data=output_zip_path)



def api_file_remove(args):
    try:
        file_path = args["path"]
        file_path = utils.path_home_filter(file_path)
        # print("删除", file_path)

        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)
        return dao.api_result_for_oc(data=dao.api_result_json())
    except Exception as e:
        return dao.api_result_for_oc(data=dao.api_result_json(code=0, msg=str(e)))


def api_file_rename(args):
    src_file = utils.path_home_filter(args["path"])
    file_rname = args["name"]
    new_file = os.path.join(os.path.dirname(src_file), file_rname)
    if src_file and file_rname:
        os.rename(src_file, new_file)
        return api_result_for_oc()


def api_file_image_crop(args):
    img_path = utils.path_home_filter(args["image"])
    rect = json.loads(args["rect"])

    if "target" in args:
        target_path = utils.path_home_filter(args["target"])
    else:
        target_path = os.path.join(utils.cache, f"{time.time()}.png")

    # print(utils.cache,target_path)

    with Image.open(img_path) as img:
        cropped_img = img.crop(rect)
        # 保存裁剪后的图像

        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        cropped_img.save(target_path)

    return api_result_for_oc(data=api_result_json(data=target_path))


def api_files(args):
    # print(args)
    path = utils.path_home_filter(args["path"])
    return api_result_for_oc(data=dao.api_result_json(data=file_utils.get_module_files({}, path)))
