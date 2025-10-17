import importlib
import os.path
import sys

import requests
from ascript.ios.developer.api import utils, data

key = None


def download(url, filename):
    try:
        # 发送GET请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果请求返回不成功的状态码，则抛出HTTPError异常
        # 打开一个文件用于写入
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                # 如果chunk为空，则结束循环
                if chunk:
                    file.write(chunk)

        print(f'文件已保存到 {filename}')
    except requests.RequestException as e:
        print(f'下载文件时发生错误: {e}')


def run_line(**args):
    app_id = args['id']
    file_path = args['filePath']
    file_md5 = args['fileMd5']

    data.line_id = app_id
    download_file = os.path.join(utils.cache, "download.as")
    download(file_path, download_file)
    module_name = f"line{app_id}"

    utils.r_name = module_name
    utils.r_root = os.path.join(utils.module_line, utils.r_name)

    # R.name = utils.r_name
    # R.root = utils.r_root

    line_file = os.path.join(utils.module_line, module_name)
    utils.unzip_file(download_file, line_file)
    sys.path.append(utils.module_line)

    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = importlib.import_module(module_name)
