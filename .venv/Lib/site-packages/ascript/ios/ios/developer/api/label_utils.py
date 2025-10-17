import ast
import json
import os.path
import re
import shutil
import zipfile

from ascript.ios.developer.api import utils

labelsDirName = "labels"
labelsStr = "tag.txt"


def add_label(label: str):
    fixed_data_str = label.replace("'", '"')
    label_dao = json.loads(fixed_data_str)
    # print(label_dao)
    lable_dir_name = label_dao["module"]
    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    label_dir = os.path.join(label_root_dir, labelsDirName)
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)
    label_txt = os.path.join(label_dir, label_dao["image"].split('.')[0] + ".txt")
    label_pos = get_label_pos(lable_dir_name, label_dao["name"])
    content = f"{label_pos} {label_dao['x']} {label_dao['y']} {label_dao['w']} {label_dao['h']}"
    if os.path.exists(label_txt):
        file_size = os.path.getsize(label_txt)
    else:
        file_size = 0
    if file_size > 0:
        content = f"\r\n{content}"
    with open(label_txt, 'a', encoding='utf-8') as file:
        file.write(content)

    return True


def get_label_pos(lable_dir_name, label_name):
    label_names = get_label_names(lable_dir_name)
    for index, name in enumerate(label_names):
        if name == label_name:
            return index

    add_lable_name(lable_dir_name, label_name)
    return len(label_names)


def get_label_names(lable_dir_name):
    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    tag_file = os.path.join(label_root_dir, labelsStr)
    if not os.path.exists(label_root_dir):
        os.makedirs(label_root_dir)

    if not os.path.exists(tag_file):
        return []

    with open(tag_file, 'r', encoding='utf-8') as file:
        second_line = None
        for i, line in enumerate(file, start=1):
            if i == 2:
                second_line = line
                break

    if second_line:
        match = re.search(r'names:\s*\[(.*?)\]', second_line)
        if match:
            # 使用 ast.literal_eval() 安全地解析出列表
            # 注意：这里我们不需要对 match.group(1) 进行额外的处理，因为 ast.literal_eval() 会正确地解析出列表
            names_list = ast.literal_eval(f'[{match.group(1)}]')
        else:
            names_list = []
    else:
        names_list = []

    return names_list


def add_lable_name(lable_dir_name, label_name):
    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    if not os.path.exists(label_root_dir):
        os.makedirs(label_root_dir)
    tag_file = os.path.join(label_root_dir, labelsStr)

    label_names = get_label_names(lable_dir_name)
    label_names.append(label_name)
    content = f"nc: {len(label_names)}\r\nnames: {json.dumps(label_names)}"
    with open(tag_file, 'w', encoding='utf-8') as file:
        file.write(content)


def get_img_lables(lable_dir_name, img_name: str):
    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    label_dir = os.path.join(label_root_dir, labelsDirName)
    lable_txt = os.path.join(label_dir, f"{img_name.split('.')[0]}.txt")
    lables_res = []
    try:
        with open(lable_txt, 'r', encoding='utf-8') as file:
            for line in file:
                ll = line.strip().split(" ")
                # print(ll)
                label = {
                    "pos": int(ll[0]),
                    "x": float(ll[1]),
                    "y": float(ll[2]),
                    "w": float(ll[3]),
                    "h": float(ll[4]),
                }
                lables_res.append(label)
    except FileNotFoundError:
        print(f"The file {lable_txt} does not exist.")

    return lables_res


def export_cnp(lable_dir_name):
    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    output_zip_path = os.path.join(label_root_dir, f"{lable_dir_name}.cnp")

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

    return output_zip_path


def excport_yolo_zip(lable_dir_name):
    root_dir = os.path.join(utils.label_yolo_space, lable_dir_name)
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    py_train = os.path.join(root_dir, "train.py")
    yolo_train_fill_content(py_train)

    label_root_dir = os.path.join(utils.label_space, lable_dir_name)
    tag_file = os.path.join(label_root_dir, labelsStr)
    targ_tag_file = os.path.join(root_dir, labelsStr)
    shutil.copy2(tag_file, targ_tag_file)
    rootDataSet = os.path.join(root_dir, "datasets")

    images_dir = os.path.join(rootDataSet, "images")
    images_train_dir = os.path.join(images_dir, "train")
    images_val_dir = os.path.join(images_dir, "val")

    labels = os.path.join(rootDataSet, "labels")
    labels_train_dir = os.path.join(labels, "train")
    labels_val_dir = os.path.join(labels, "val")
    yaml = os.path.join(rootDataSet, "data.yaml")

    os.makedirs(images_train_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)

    os.makedirs(labels_train_dir, exist_ok=True)
    os.makedirs(labels_val_dir, exist_ok=True)

    yolo_yaml_fill(yaml, lable_dir_name)

    # 拷贝图像
    label_image_dir = os.path.join(label_root_dir, "images")
    label_label_dir = os.path.join(label_root_dir, "labels")

    file_images = os.listdir(label_image_dir)
    for filename in file_images:
        src_file = os.path.join(label_image_dir, filename)
        dst_file = os.path.join(images_train_dir, filename)
        shutil.copy2(src_file, dst_file)

    shutil.copy2(os.path.join(label_image_dir, file_images[0]), os.path.join(images_val_dir, os.path.basename(file_images[0])))

    file_labels = os.listdir(label_label_dir)
    for filename in file_labels:
        src_file = os.path.join(label_label_dir, filename)
        dst_file = os.path.join(labels_train_dir, filename)
        shutil.copy2(src_file, dst_file)

    shutil.copy2(os.path.join(label_label_dir, file_labels[0]), os.path.join(labels_val_dir, os.path.basename(file_labels[0])))

    output_zip_path = os.path.join(utils.label_yolo_space,f"{lable_dir_name}.zip")

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(root_dir):
            # 对于根目录下的文件，直接使用文件名作为arcname
            if root == label_root_dir:
                arcname_root = ''
            else:
                # 对于子目录中的文件，使用相对于根目录的路径（去掉根目录名本身）
                arcname_root = os.path.relpath(root, root_dir)
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

    return output_zip_path


def yolo_yaml_fill(file_path, lable_dir_name):
    names = get_label_names(lable_dir_name)

    content = f'''
path: .
train: images/train
val: images/val
test: 
nc: {len(names)}  
# Classes
names:
    '''
    for index, name in enumerate(names):
        content = content + f"\r\n  {index}: {name}"

    with open(file_path, 'w', encoding='utf-8') as file:
        # 追加内容到文件
        file.write(content)


def yolo_train_fill_content(path):
    centent = '''
# 环境配置步骤,创建一个新的python环境,用conda也可以
# 1.安装pytorch 官网地址：https://pytorch.org/ 可在下方生成pip 进行安装
# 2.安装yolo库 :pip install ultralytics==8.3.31
# 3.点击运行即可
# 4.训练完成后，把 model.ncnn.bin 和 model.ncnn.param 放置AScript工程下，加载即可 nc参数可查看data.yarm

from ultralytics import YOLO
model = YOLO("yolov8n.pt")
train_results = model.train(
    data="./datasets/data.yaml",  # path to dataset YAML
    epochs=300,  # number of training epochs
    imgsz=640,  # training image size
    device="cpu",  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
)
print("训练结束")
path = model.export(format="ncnn")
print("转换地址",path)'''

    with open(path, 'w', encoding='utf-8') as file:
        # 追加内容到文件
        file.write(centent)
