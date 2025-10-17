import os.path
import subprocess
import zipfile

from PyQt5.QtCore import QThread, pyqtSignal
from ascript.windows.client import tools


class PkgThread(QThread):
    def __init__(self):
        super().__init__()
        self.package_path = None

    def set_package_path(self, package_path):
        self.package_path = package_path

    def run(self):
        req_txt_file = os.path.join(self.package_path, "requirements.txt")
        str_cmd = f"workon {tools.get_virtualenv_cureent()}\n pip freeze > {req_txt_file}\n"
        print(str_cmd)
        self.exec(str_cmd)

        try:
            zip_path = os.path.join(self.package_path, os.path.basename(self.package_path) + ".wac")

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.package_path):
                    if ".idea" in root or '__pycache__' in root or '.git' in root:
                        print(root)
                        continue
                    for file in files:
                        file_path = os.path.join(root, file)

                        if os.path.splitext(file_path)[1] != ".wac":
                            zipf.write(file_path, os.path.relpath(file_path, self.package_path))

            os.startfile(self.package_path)
        except Exception as e:
            print(str(e))

    def exec(self, cmd: str):
        try:
            with subprocess.Popen("cmd", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc:
                cmd = cmd.encode()
                proc.stdin.write(cmd)
                proc.stdin.flush()
                proc.stdin.close()

                infos = []
                errors = []
                for line in proc.stdout:
                    infos.append(line.strip())
                    # print(line.strip())
                    # self.log_info.emit(line.strip())

                for line in proc.stderr:
                    errors.append(line.strip())
                    # print(line.strip())
                    # self.log_error.emit(line.strip())

            return [proc.returncode, infos, errors]
        except Exception as e:
            print(str(e))


class PyEnvSet(QThread):
    set_statue = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.key = None
        self.value = None

    def setkv(self, key, value):
        self.key = key
        self.value = value

    def run(self):
        try:
            res = set_env(self.key, self.value)
            self.set_statue.emit(res)
        except Exception as e:
            print(str(e))


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
