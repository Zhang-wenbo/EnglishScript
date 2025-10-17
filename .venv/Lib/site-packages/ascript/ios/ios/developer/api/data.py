import base64
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from ascript.ios import system
from ascript.ios.developer.api import utils, oc

# import utils

# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# key = "PDH@BDT#YRG@2023"
# iv = "$QWV#AHF@LKJ!QWC"

line_id = None


def get_md5(msg: str):
    md5 = hashlib.md5()
    md5.update(msg.encode('utf-8'))
    return md5.hexdigest()


def get_md5_file(file_path: str):
    with open(file_path, 'rb') as f:
        data = f.read()

    md5_hash = hashlib.md5()
    md5_hash.update(data)
    md5 = md5_hash.hexdigest()
    return md5


# def aes_encrypt(plain_text: str):
#     key = "PDH@BDT#YRG@2023".encode()
#     iv = "$QWV#AHF@LKJ!QWC".encode()
#     # plain_text = '{"appId":"-1","appName":"AirScript","dataId":"971130ac-0896-42a4-ac62-bb30d042975a","deviceId":"20625f7f-d155-4d24-8bff-b61b5e87d12b","packageName":"com.aojoy.airscript","version":"2145","versionName":"2.1.45"}'
#     plain_text = plain_text.encode()
#     try:
#         cipher = AES.new(key, AES.MODE_CBC, iv)
#         encrypted_text = cipher.encrypt(pad(plain_text, AES.block_size))
#             b64_text = base64.b64encode(encrypted_text)
#         return b64_text.decode()
#     except Exception as e:
#         print(str(e))
#
#
# def ase_decrypt(cipher_text: str):
#     try:
#         key = "PDH@BDT#YRG@2023".encode()
#         iv = "$QWV#AHF@LKJ!QWC".encode()
#         cipher_text = base64.b64decode(cipher_text)
#         cipher = AES.new(key, AES.MODE_CBC, iv)
#         decrypted_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
#         return decrypted_text.decode()
#     except Exception as e:
#         print(str(e))


def aes_encrypt(plain_text: str, dkey: str, div: str):
    dkey = dkey.encode()
    div = div.encode()

    # 确保plain_text是bytes类型
    plain_text = plain_text.encode()

    # 使用PKCS7填充（cryptography库内部处理）
    padder = padding.PKCS7(128).padder()  # AES块大小为128位
    padded_data = padder.update(plain_text) + padder.finalize()

    # 创建Cipher实例并加密
    cipher = Cipher(algorithms.AES(dkey), modes.CBC(div), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_text = encryptor.update(padded_data) + encryptor.finalize()

    # 将加密后的数据编码为Base64字符串
    b64_text = base64.b64encode(encrypted_text).decode()

    return b64_text


def aes_decrypt(cipher_text: str, dkey: str, div: str):
    dkey = dkey.encode()
    div = div.encode()

    # 将Base64编码的字符串解码为bytes
    cipher_text = base64.b64decode(cipher_text)

    # 创建Cipher实例并解密
    cipher = Cipher(algorithms.AES(dkey), modes.CBC(div), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_text = decryptor.update(cipher_text) + decryptor.finalize()

    # 移除PKCS7填充
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_text = unpadder.update(padded_text) + unpadder.finalize()

    # 将bytes解码为字符串
    return decrypted_text.decode()


def eout_f(file_name, key):
    print(file_name, key)
    with open(file_name, 'r', encoding='utf-8') as file:
        # 读取文件全部内容
        content = file.read()
        base64_encoded_str = aes_decrypt(content, key, 'iUJM^YHN%TGB$RFV')
        print(file)
        # 解码Base64字符串
        decoded_bytes = base64.b64decode(base64_encoded_str)

        # 使用'wb'模式打开文件以写入二进制数据
        with open(file_name, 'wb') as f:
            f.write(decoded_bytes)


def eout(path, key=None):
    if key is None:
        key = line_id
    package_path = path.replace(".", "/")
    file = os.path.join(utils.module_line, package_path)
    # print(file)
    if os.path.isdir(file):
        file_init = os.path.join(file, "__init__.pyc")
        if os.path.exists(file_init):
            # eout_f(file_init, key)
            oc.on_efile(file_init, key)
    else:
        file_child = os.path.join(f"{file}.pyc")
        if os.path.exists(file_child):
            # eout_f(file_child, key)
            oc.on_efile(file_child, key)
    return


current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(current_dir, "assets/config.ac")


# class Config:
#     __instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls.__instance is None:
#             cls.__instance = super().__new__(cls)
#         return cls.__instance
#
#     def __init__(self):
#         if not os.path.exists(os.path.dirname(config_path)):
#             os.mkdir(os.path.dirname(config_path))
#
#         self.device_id = system.client.info.uuid
#         self.search = {}
#         self.cards = {}
#
#         self.get_config()
#
#     def to_dict(self):
#         return {
#             "device_id": self.device_id,
#             "search": self.search,
#             "cards": self.cards
#         }
#
#     def get_config(self):
#         data_dict = self.to_dict()
#         if not os.path.exists(config_path):
#             pass
#         else:
#             try:
#                 with open(config_path, "r") as f:
#                     content = f.read()
#                 data_dict = json.loads(aes_decrypt(content, key, iv))
#             except Exception as e:
#                 print(str(e))
#                 data_dict = self.to_dict()
#
#         self.device_id = data_dict['device_id']
#         self.search = data_dict['search']
#         self.cards = data_dict['cards']
#
#     def save_config(self):
#         config_json_str = json.dumps(self.to_dict())
#         with open(config_path, "w") as f:
#             f.write(aes_encrypt(config_json_str, key, iv))
