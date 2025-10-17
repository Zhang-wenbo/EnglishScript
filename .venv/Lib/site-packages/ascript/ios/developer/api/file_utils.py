import os
import time


def get_folder_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # print(fp)
            # 跳过如果它是符号链接
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    # print(total_size)
    return total_size


# 使用示例
# folder_path = '/path/to/your/folder'  # 替换为你的文件夹路径
# print(f"Folder size is: {get_folder_size(folder_path)} bytes")


# 如果你想要以更友好的格式（如 MB, GB）显示大小，可以添加转换函数
def convert_bytes(num_bytes):
    """
    将字节数转换为适当的单位（KB, MB, GB）并格式化输出。
    """
    if num_bytes >= 1024 ** 3:  # 1 GB = 1024^3 bytes
        return "{:.2f} GB".format(num_bytes / (1024 ** 3))
    elif num_bytes >= 1024 ** 2:  # 1 MB = 1024^2 bytes
        return "{:.2f} MB".format(num_bytes / (1024 ** 2))
    elif num_bytes >= 1024:  # 1 KB = 1024 bytes
        return "{:.2f} KB".format(num_bytes / 1024)
    else:
        return "{} bytes".format(num_bytes)


def get_module_files(model: dict, file):
    if not os.path.exists(file):
        return None

    model["name"] = os.path.basename(file)
    model["lastModified"] = os.path.getmtime(file)
    model["lastModified_format"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file)))
    model["length"] = os.path.getsize(file)
    model["length_format"] = convert_bytes(os.path.getsize(file))
    model["path"] = file
    model["isFile"] = os.path.isfile(file)

    if os.path.isdir(file):
        children = []
        for f in os.listdir(file):
            if f == "__pycache__":
                continue
            children.append(get_module_files({}, os.path.join(file, f)))

        model["childs"] = children

    return model
