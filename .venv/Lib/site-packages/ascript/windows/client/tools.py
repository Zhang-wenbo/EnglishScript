import os.path
import subprocess
import sys
import time
import webbrowser

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QPushButton
from ascript.windows import screen

ENV_AIRCLICK_WORKSPACE = "AIRCLICK_WORKSPACE"
ENV_AIRCLICK_VIRTUALENV = "AIRCLICK_VIRTUALENV"
ENV_HOME = "WORKON_HOME"


def tools_open():
    webbrowser.open("http://127.0.0.1:8080/colors")


def tool_capture_save() -> str:
    # pass
    img = screen.capture()

    current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # img.show()
    filename = os.path.join(current_dir, "assets/tools/capture/" + str(int(time.time())) + ".png")
    print(filename)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    return filename
    # img.save("./assets/tools/capture/"+time.time()+".png")


class ToolButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arg = {}


class EnvThread(QThread):
    statue = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.key = None
        self.value = None

    def setkv(self, k, v):
        self.key = k
        self.value = v

    def run(self):
        self.statue.emit(1)
        set_env(key=self.key, value=self.value)
        self.statue.emit(2)


def set_env(key: str, value: str) -> bool:
    try:
        # Machine 是系统，User 是用户
        subprocess.run(['powershell',
                        f'[System.Environment]::SetEnvironmentVariable("{key}","{value}", [System.EnvironmentVariableTarget]::User)'])
        subprocess.run(['echo', f'%${key}%'], shell=True)
        os.environ[f'{key}'] = value
        return True
    except Exception as e:
        print(str(e))
        return False


def get_workspace():
    workspace = os.environ.get(ENV_AIRCLICK_WORKSPACE)

    if workspace:
        return workspace

    workspace = os.path.join(os.path.expanduser("~"), "airclick_workspace")
    if not os.path.exists(workspace):
        os.mkdir(workspace)

    return workspace


def set_workspace(path: str):
    return set_env(ENV_AIRCLICK_WORKSPACE, path)


def get_virtualenv_cureent():
    return os.environ.get(ENV_AIRCLICK_VIRTUALENV)


def get_virtualenv_list():
    vs_list = []
    v_home = os.environ.get(ENV_HOME)
    v_current_home = os.environ.get(ENV_AIRCLICK_VIRTUALENV)
    if v_home is None:
        v_home = os.path.expanduser("~\\Envs")
        print(v_home)

    if v_current_home is None:
        v_current_home = "ascript"

    vs = os.listdir(v_home)

    for v in vs:
        exe_file = os.path.join(v_home, v, "Scripts", 'python.exe')
        # print(exe_file)
        if os.path.exists(exe_file):
            is_current = v_current_home == v
            vdao = {'name': os.path.basename(v), 'python': exe_file, 'is_current': is_current}
            vs_list.append(vdao)

    return vs_list
