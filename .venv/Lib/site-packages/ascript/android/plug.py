from airscript.system import Plug as asPlug


def load(plug_and_version: str):
    return asPlug.load(plug_and_version)


def load_apk(file_path: str):
    return asPlug.load_apk(file_path)
