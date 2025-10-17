import ctypes
import json
import os.path
import platform
import signal
import subprocess
import threading
import pyautogui
import win32api
import win32con
import win32gui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QEvent
from PyQt5.QtGui import QCursor, QPixmap, QIcon, QEnterEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QFrame, QFileDialog, QDialog, QHBoxLayout, QLabel, QCommandLinkButton, \
    QSpacerItem, QMessageBox

from PyQt5.uic import loadUiType, loadUi
import sys

from ascript.windows import window
from ascript.windows.client import tools
import configparser
from ascript.windows.client.tools import EnvThread
from ascript.windows.client.worker import PkgThread, PyEnvSet

# Load the UI file
current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
# current_dir = os.path.dirname(__file__)
ui_bar_path = os.path.join(current_dir, "assets\pyui/bar.ui")
ui_step_path = "assets/pyui/step.ui"
ui_workspace_path = "assets/pyui/workspace.ui"
ui_pycharm_path = "assets/pyui/pycharminstall.ui"
ui_pyinstaller_path = os.path.join(current_dir, "assets/pyui/pyinstall.ui")
ui_home_path = "assets/pyui/home.ui"
ui_log_path = "assets/pyui/log.ui"
ui_app_item_path = "assets/pyui/item_app.ui"
ui_config_path = os.path.join(current_dir, "assets/pyui/home.ui")
ui_hwnd_path = os.path.join(current_dir, "assets/pyui/hwnd.ui")

py_388_path = "assets/data/python-3.8.8.exe"

py_work_config = "assets/tools/config.init"

py_apps_quick_start = ui_pyinstaller_path = os.path.join(current_dir, "assets/tools/apps")


# ui_img_bar = [os.path.join(current_dir,"assets/img/ico_run.png"),os.path.join(current_dir,"assets/img/ico_stop.png")]


class AirIcon(QIcon):
    def __init__(self, name: str):
        path = os.path.join(current_dir, "assets/img", name)
        super().__init__(path)


class BarWindow(QFrame):
    _instance = None
    log_window = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        super().__init__()
        self.is_dragging = False
        loadUi(ui_bar_path, self)
        try:
            # self.home_window = HomeWindow()
            self.config_window = None
            self.hwnd_window = HwndWindow()
        except Exception as e:
            print(str(e))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # 悬浮在最顶部
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明
        self.capture.clicked.connect(self.btn_capture)
        self.tools.clicked.connect(tools.tools_open)
        self.config.clicked.connect(self.btn_config)
        # self.logs.clicked.connect(self.btn_logs)
        # self.app.clicked.connect(self.btn_local_apps)
        self.btn_min.clicked.connect(self.btn_min_click)
        self.btn_close.clicked.connect(self.btn_close_click)
        self.hwnd.clicked.connect(self.btn_hwnd_click)

        self.ico.mousePressEvent = self.ico_down_event
        self.ico.mouseMoveEvent = self.ico_move_event
        self.ico.mouseReleaseEvent = self.ico_up_event
        self.menulabels = []
        self.menubuttons = [self.capture, self.tools, self.config, self.btn_min, self.btn_close,
                            self.labele_quick, self.hwnd]
        self.move_thread = None

        # self.run.clicked.connect()

        self.capture_context_num = 0

        self.auto_close_menu_time = 5
        self.start_auto_move_side_logic()

        # self.run_satue = [AirIcon("ico_run.png"), AirIcon("ico_stop.png")]

        w, h = pyautogui.size()
        self.move(w - 160, h / 2 - 170)

        self.enterEvent(None)

        # 快捷按键 与hwnd

        quick_keys = [
            {'tip': "CTRL+F1", 'keys': [win32con.VK_CONTROL, win32con.VK_F1], 'btn': 'capture',
             'fun': self.btn_capture},
            {'tip': "CTRL+F2", 'keys': [win32con.VK_CONTROL, win32con.VK_F2], 'btn': 'tools',
             'fun': tools.tools_open},
            {'tip': "CTRL+F3", 'keys': [win32con.VK_CONTROL, win32con.VK_F3], 'btn': 'hwnd',
             'fun': self.btn_hwnd_click},
        ]
        self.quick_keys = quick_keys

        self.qkey_timer = QTimer(self)
        self.qkey_timer.timeout.connect(self.on_qkey_all)
        self.qkey_timer.start(100)

        labele_quick = self.labele_quick

        def menu_enterEvent(self, event):
            btn_name = self.objectName()
            for key in quick_keys:
                if key['btn'] == btn_name:
                    labele_quick.setText(key['tip'])

        def menu_leaveEvent(self, event):
            labele_quick.setText("")

        for menu_btn in self.menubuttons:
            menu_btn.enterEvent = menu_enterEvent.__get__(menu_btn, QCommandLinkButton)
            menu_btn.leaveEvent = menu_leaveEvent.__get__(menu_btn, QCommandLinkButton)

        self.tip_win32()

    def tip_win32(self):
        if '64' not in platform.machine():
            QMessageBox.information(self, "32位提示",
                                    f"您的电脑为32位，当前版本下，OCR无法使用(64位可用)")

    def btn_enterEvent(self, event=None):
        print(self.objectName())

    def on_qkey_all(self):
        for key_dao in self.quick_keys:
            true_key = True
            for key in key_dao['keys']:
                if not win32api.GetAsyncKeyState(key):
                    true_key = False
                    break
            if true_key:
                key_dao['fun']()

        if self.hwnd_window.isVisible():
            active_win = window.find()
            print(active_win)
            self.hwnd_window.change_hwnd(active_win)

        # if win32api.GetAsyncKeyState(win32con.VK_CONTROL) and win32api.GetAsyncKeyState(win32con.VK_F1):
        #     # CTRL+F1 ,截图
        #     self.btn_capture()
        #
        # if win32api.GetAsyncKeyState(win32con.VK_CONTROL) and win32api.GetAsyncKeyState(win32con.VK_F2):
        #     # CTRL+F1 ,截图
        #     tools.tools_open()
        #
        # if win32api.GetAsyncKeyState(win32con.VK_CONTROL) and win32api.GetAsyncKeyState(win32con.VK_F3):
        #     # CTRL+F1 ,截图
        #     self.btn_local_apps()

    def btn_min_click(self):
        self.showMinimized()

    def btn_close_click(self):
        self.close()

    def btn_hwnd_click(self):
        self.hwnd_window.show()

    def btn_config(self):
        self.btn_local_apps()
        self.config_window = ConfigWindow()
        self.config_window.show()

    def enterEvent(self, event):
        self.__show_menu()
        self.frame.setStyleSheet("background-color: #90000000;border-radius:10px;")

        for btn in self.menubuttons:
            btn.setStyleSheet(
                "QCommandLinkButton:hover{background:#B0000000;} QCommandLinkButton{background:#00000000;color:white;border-radius:0px;min-height:60px;min-width:100px}")
        # self.label_capture.setStyleSheet("QLabel{color:white;background:#90FFFFFF; border-radius:10px;padding:5px}")

        self.btn_min.setStyleSheet(
            "QToolButton:hover{background:#B0000000} QToolButton{background:#00000000;color:white;border-radius:0px;margin-top:10px;}")
        self.btn_close.setStyleSheet(
            "QToolButton:hover{background:#B0000000} QToolButton{background:#00000000;color:white;border-radius:0px;margin-top:10px;}")

        self.labele_quick.setStyleSheet(
            "QLabel{background:#00000000;color:white;border-radius:0px;margin-top:10px;}")

    def leaveEvent(self, event):
        self.__hide_menu()
        self.frame.setStyleSheet("background-color: #00000000;border-radius:10px;")
        # self.__auto_move_side()

    def set_run_statue(self, statue: bool, num: int):
        print('?statue')
        pass

    def ico_down_event(self, event):
        if event.button() == Qt.LeftButton:
            self.ico_down_pos = QCursor.pos()
            self.offset = self.ico.pos() + event.pos()
            self.is_dragging = True

    def ico_move_event(self, event):
        if self.is_dragging:
            mouse_pos = QCursor.pos()
            self.move(mouse_pos.x() - self.offset.x(), mouse_pos.y() - self.offset.y())
            # new_pos = event.pos() - self.offset
            # self.move(new_pos)
            # self.offset = event.pos() - self.frameGeometry().topLeft()
            # print(event)

    def ico_up_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            temp_pos = QCursor.pos() - self.ico_down_pos
            if abs(temp_pos.x()) < 5 and abs(temp_pos.y()) < 5:
                self.start_auto_move_side_logic()

    def start_auto_move_side_logic(self):
        self.auto_close_menu_time = 5
        self.__show_menu()

    def __auto_move_side(self):
        pass

    def __hide_menu(self):
        for l in self.menulabels:
            l.setVisible(False)

        self.capture_context_num = 0

        for b in self.menubuttons:
            b.setVisible(False)

    def __show_menu(self):
        self.capture.setText("截图")
        for l in self.menulabels:
            l.setVisible(True)

        for b in self.menubuttons:
            b.setVisible(True)

    def btn_local_apps(self):

        if not os.path.exists(py_apps_quick_start):
            os.mkdir(py_apps_quick_start)

        # 生成快捷方式
        file_list = get_workspace_list()
        for f in file_list:
            pyrun_file = os.path.join(f, "__init__.py")
            if not os.path.exists(pyrun_file):
                pyrun_file = os.path.join(f, "main.py")
                if not os.path.exists(pyrun_file):
                    continue

            exe_file = os.path.join(py_apps_quick_start, os.path.basename(f) + ".bat")
            print(exe_file)
            with open(exe_file, 'w') as exe_bat:
                exe_bat.write("@echo off\n")
                exe_bat.write(f'cmd /k "workon ascript && python {pyrun_file}"')

        # os.startfile(py_apps_quick_start)

    def btn_home(self):
        try:
            self.home_window.show()
            self.home_window.setWindowState(Qt.WindowActive)
        except Exception as e:
            print(str(e))

    def btn_logs(self):
        try:
            BarWindow.log_window.show()
        except Exception as e:
            print(str(e))

    def btn_capture(self):
        # self.capture.setEnabled(False)
        # self.start_auto_move_side_logic()
        self.capture.setVisible(True)
        tools.tool_capture_save()
        self.capture_context_num += 1
        self.capture.setText("截图 " + str(self.capture_context_num))

        # self.capture_progress.setVisible(True)
        # def run_progress():
        #     progress_value = 0
        #
        #     while progress_value < 101:
        #         self.capture_progress.setValue(progress_value)
        #         time.sleep(0.01)
        #         progress_value += 5
        #
        #     self.capture_progress.setVisible(False)
        #
        # threading.Thread(target=run_progress).start()


class HwndWindow(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(current_dir, ui_hwnd_path), self)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.label_hwnd.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_name.setTextInteractionFlags(Qt.TextSelectableByMouse)

        size = pyautogui.size()

        self.move(size.width - self.width() - 10, 10)

    def change_hwnd(self, active_win):
        if active_win:
            self.label_hwnd.setText(str(active_win.hwnd))
            self.label_title.setText(str(active_win.title))
            self.label_name.setText(str(active_win.name))
        else:
            self.label_hwnd.setText('')
            self.label_title.setText('')
            self.label_name.setText('')


class ConfigWindow(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(ui_config_path, self)
        # self.setWindowTitle("")
        self.env_thread = EnvThread()
        self.pkg_thread = PkgThread()
        self.env_thread.statue.connect(self.env_thread_statue)
        if tools.get_workspace():
            self.config_work.setText(tools.get_workspace())
        else:
            self.config_work.setText("请立即设置环境变量")

        self.config_work.clicked.connect(self.btn_config_work)

        self.comboBox.currentIndexChanged.connect(self.current_env_change)
        self.envlist = []
        self.set_env_list()
        self.label_path_exe.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.btn_menu_app.clicked.connect(self.btn_menu_app_click)
        self.btn_menu_config.clicked.connect(self.btn_menu_config_click)

        # self.pages.setCurrentIndex(1)
        self.set_page(0)
        self.run_satue = [AirIcon("ico_run.png"), AirIcon("ico_stop.png")]

        self.worker = {}

        self.app_chilren_views = []

        self.addData()

    def btn_menu_app_click(self):
        self.set_page(0)

    def btn_menu_config_click(self):
        self.set_page(1)

    def set_page(self, current_page: int):
        pages = [(self.btn_menu_app, self.page_1), (self.btn_menu_config, self.page_2)]

        for i in range(len(pages)):
            if i == current_page:
                self.pages.setCurrentWidget(pages[i][1])
                # 设置样式
                pages[i][0].setStyleSheet(
                    "QCommandLinkButton{min-height:60px;min-width:100px;border:none;border-radius:15px;background:#d1e7e2}")
            else:
                pages[i][0].setStyleSheet(
                    "QCommandLinkButton{min-height:60px;min-width:100px;border:none;border-radius:15px;background:#00000000}QCommandLinkButton:hover{min-height:60px;min-width:100px;border:none;border-radius:15px;background:#d1e7e2}")

    def current_env_change(self, index):
        envdao = self.envlist[index]
        self.env_thread.setkv(tools.ENV_AIRCLICK_VIRTUALENV, envdao['name'])
        self.label_path_exe.setText(envdao['python'])
        self.env_thread.start()

    def set_env_list(self):
        self.envlist = tools.get_virtualenv_list()
        for item in self.envlist:
            if item['is_current']:
                self.comboBox.setCurrentText(item['name'])
                self.label_path_exe.setText(item['python'])

            self.comboBox.addItem(item['name'])

    def btn_config_work(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        if file_dialog.exec_() == QFileDialog.Accepted:
            select_folder = file_dialog.selectedFiles()[0]
            self.config_work.setText(select_folder)
            self.env_thread.setkv(tools.ENV_AIRCLICK_WORKSPACE, select_folder)
            self.env_thread.start()

    def env_thread_statue(self, statue: int):
        if statue == 2:
            print('结束')

    def enterEvent(self, event):
        super().enterEvent(event)
        # self.addData()

    def addData(self):
        # 加载一下
        # self.scrool_apps_contain.r

        try:
            for v in self.app_chilren_views:
                self.app_scroll.removeWidget(v)
                # v.deleteLater()

            self.app_scroll.update()

            self.work_dir = tools.get_workspace()
            self.app_list = []
            # app_scroll
            for filename in os.listdir(self.work_dir):
                file_item = os.path.join(self.work_dir, filename)
                if os.path.isdir(file_item):
                    item_view = self.create_item(file_item)
                    self.app_chilren_views.append(item_view)
                    self.app_scroll.addWidget(item_view)

        except Exception as e:
            print(str(e))

    def create_item(self, file: str):

        app_name = os.path.basename(file)

        def itme_run_click(run_btn):
            print(run_btn, app_name)

            exe_file = os.path.join(py_apps_quick_start, app_name + ".bat")
            win_handle = win32api.ShellExecute(0, 'open', 'cmd', f'/c {exe_file}', '', 1)
            # os.system("D:\\work\\airclick_pylib\\ascript\\windows\\client\\assets\\tools\\apps\\first.bat")

        def itme_package_click(run_btn):
            print(run_btn, app_name)
            pak_dir = os.path.join(tools.get_workspace(), app_name)
            if not self.pkg_thread.isRunning():
                self.pkg_thread.set_package_path(pak_dir)
                self.pkg_thread.start()

        frame = loadUi(os.path.join(current_dir, ui_app_item_path), None)
        frame.label.setText(app_name)

        try:
            if app_name in self.worker:
                if self.worker[app_name].isRunning():
                    frame.run_btn.setIcon(self.run_satue[1])
                else:
                    frame.run_btn.setIcon(self.run_satue[0])
            else:
                frame.run_btn.setIcon(self.run_satue[0])
        except Exception as e:
            print(str(e))

        frame.run_btn.clicked.connect(lambda checked: itme_run_click(frame.run_btn))
        frame.package_btn.clicked.connect(lambda checked: itme_package_click(frame.package_btn))
        return frame


class WorkSpaceWindow(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(current_dir, ui_workspace_path), self)
        self.env_thread = PyEnvSet()


        self.btn_worksapce_choose.clicked.connect(self.worksapce_choose)



    def worksapce_choose(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.label_info.setText("正在设置中,请稍后...")
            select_folder = file_dialog.selectedFiles()[0]
            self.input_worksaoce_des.setText(select_folder)
            print(select_folder)
            self.env_thread.setkv(tools.ENV_AIRCLICK_WORKSPACE, select_folder)
            self.env_thread.start()
            # self.close()


class HomeWindow(QFrame):
    _instance = None
    log_window = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        super().__init__()
        loadUi(os.path.join(current_dir, ui_home_path), self)
        self.work_dir = ""
        self.app_list = []
        self.win_workspace = WorkSpaceWindow()
        self.setting_work.clicked.connect(self.fun_setting_work)
        self.setting_python.clicked.connect(self.fun_setting_python)
        self.label_work.setText(check_workspace()[1])
        self.label_py.setText(sys.executable)

        self.run_satue = [AirIcon("ico_run.png"), AirIcon("ico_stop.png")]

        self.worker = {}

    def on_run_statue(self, statue: bool):
        print(statue)
        self.addData()

        run_works = 0

        for work in self.worker:
            if self.worker[work].isRunning():
                run_works += 1

        if run_works > 0:
            BarWindow.get_instance().set_run_statue(True, run_works)
        else:
            BarWindow.get_instance().set_run_statue(False, run_works)

    def on_log_info(self, text):
        BarWindow.log_window.add_log(text)

    def on_log_error(self, text):
        BarWindow.log_window.add_log(text)

    def fun_setting_work(self):
        self.win_workspace.show()

    def fun_setting_python(self):
        self.win_pyinstall.show()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.addData()

    def addData(self):
        # 加载一下
        # self.scrool_apps_contain.r

        while self.scrool_apps_contain.rowCount() > 0:
            self.scrool_apps_contain.takeRow(0)

        workSpace, self.work_dir = check_workspace()
        self.app_list = []
        # scrool_apps_contain
        for filename in os.listdir(self.work_dir):
            file_item = os.path.join(self.work_dir, filename)
            if os.path.isdir(file_item):
                self.scrool_apps_contain.addRow(self.create_item(file_item))
                # pass
                # self.create_item(file_item)

        # self.

    def create_item(self, file: str):

        app_name = os.path.basename(file)

        def tool_click(run_btn):
            print(run_btn)
            if app_name in self.worker:
                runner = self.worker[app_name]
                if runner.isRunning():
                    print('stop')
                    try:
                        runner.stop()
                    except Exception as e:
                        print(str(e))
                else:
                    runner.start()
            else:
                runner = RunThread(file)
                runner.run_statue.connect(self.on_run_statue)
                runner.log_info.connect(self.on_log_info)
                runner.log_error.connect(self.on_log_error)
                self.worker[runner.name] = runner
                runner.start()

        frame = loadUi(os.path.join(current_dir, ui_app_item_path), None)
        frame.label.setText(app_name)

        try:
            if app_name in self.worker:
                if self.worker[app_name].isRunning():
                    frame.run_btn.setIcon(self.run_satue[1])
                else:
                    frame.run_btn.setIcon(self.run_satue[0])
            else:
                frame.run_btn.setIcon(self.run_satue[0])
        except Exception as e:
            print(str(e))

        frame.run_btn.clicked.connect(lambda checked: tool_click(frame.run_btn))
        return frame


class LogWindow(QFrame):
    max_lines = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(current_dir, ui_log_path), self)

    def add_log(self, msg: str):
        if self.form_log.rowCount() >= 10:
            self.form_log.removeRow(0)

        l_t = QLabel(self)
        l_t.setText("时间")
        l_msg = QLabel(self)
        l_msg.setText(msg)
        l_msg.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.form_log.addRow(l_t, l_msg)
        vbar = self.scrollArea.verticalScrollBar()
        vbar.setValue(vbar.maximum())


class RunThread(QThread):
    log_info = pyqtSignal(str)
    log_error = pyqtSignal(str)
    run_statue = pyqtSignal(bool)

    def __init__(self, path_file: str):
        super().__init__()
        self.proc = None
        self.path = path_file
        self.name = os.path.basename(self.path)

    def pause(self):
        if self.proc:
            self.proc.suspend()

    def stop(self):
        if self.proc:
            print('stop')
            # self.proc.terminate()
            os.kill(self.proc.pid, signal.CTRL_C_EVENT)

    def run(self) -> None:
        self.run_statue.emit(True)
        main_file = os.path.join(self.path, 'main.py')
        main_file = main_file.replace('\\', '/')
        # if os.path.exists(main_file):
        #     try:
        #         print(main_file)
        #         with subprocess.Popen(['cmd', 'python', main_file], stdout=subprocess.PIPE,
        #                               stderr=subprocess.PIPE) as self.proc:
        #             for line in self.proc.stdout:
        #                 print("?-" + line.decode('utf-8').strip())  # 打印标准输出的一行
        #                 self.log_info.emit(line.decode('utf-8').strip())
        #
        #             for line in self.proc.stderr:
        #                 # log_win.add_log(line.decode('utf-8').strip())
        #                 print(line.decode('utf-8').strip())  # 打印标准错误的一行
        #                 self.log_error.emit(line.decode('utf-8').strip())
        #     except Exception as e:
        #         print(str(e))

        # self.exec(f'python {main_file}\n')

        os.startfile(os.path.dirname())

        # self.proc = subprocess.Popen(["cmd.exe"],shell=True)

        self.name = None
        self.run_statue.emit(False)

    def exec(self, cmd: str):

        try:
            with subprocess.Popen("cmd", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, encoding='cp936') as self.proc:

                self.proc.stdin.write(cmd)
                self.proc.stdin.flush()
                self.proc.stdin.close()

                for line in self.proc.stdout:
                    print(line.strip())
                    # self.proc.terminate()
                    # self.log_info.emit(line.strip())

                for line in self.proc.stderr:
                    print(line.strip())
                    # self.log_error.emit(line.strip())

            return [self.proc.returncode]
        except Exception as e:
            print(str(e))


def enter():
    try:
        app = QApplication(sys.argv)



        step3 = check_workspace()

        # 检测完毕后，再打开悬浮窗口
        if step3:
            bar_window = BarWindow()
            bar_window.show()
        else:
            def mysi(istrue):
                print('123')
                if workspace_win:
                    workspace_win.close()
                    bar_window = BarWindow()
                    bar_window.show()

            workspace_win = WorkSpaceWindow()
            workspace_win.env_thread.set_statue.connect(mysi)
            workspace_win.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(str(e))


def choose_andsetting_env(intput_view, callback):
    def child_run():
        try:
            res = subprocess.run([select_file, "--version"])
            if res:
                select_dir = os.path.dirname(select_file)
                select_dir = select_dir.replace('/', '\\')
                # 设置环境变量
                # Machine 是系统，User 是用户
                subprocess.run(['powershell',
                                f'[System.Environment]::SetEnvironmentVariable("Path","{select_dir}" +";" + $env:Path, [System.EnvironmentVariableTarget]::Machine)'])
                subprocess.run(['echo', '%PATH%'], shell=True)

                # 设置当前进程环境变量
                current_path = os.environ['PATH']
                os.environ['PATH'] = select_dir + ";" + current_path
                callback(True, "")
        except Exception as e:
            callback(False, str(e))

    file_dialog = QFileDialog()
    if file_dialog.exec_() == QDialog.Accepted:
        select_file = file_dialog.selectedFiles()[0]
        intput_view.setText(select_file)
        threading.Thread(target=child_run).start()


def set_workspace(path: str):
    try:
        work_config_file = os.path.join(current_dir, py_work_config)
        config = configparser.ConfigParser()
        config['workspace'] = {'path': path}
        with open(work_config_file, 'w') as configfile:
            config.write(configfile)

        return True
    except Exception as e:
        print(str(e))
        return False


def check_workspace():
    if tools.get_workspace():
        return True
    else:
        return False


def get_workspace_list():
    work_dir = tools.get_workspace()
    app_list = []
    # scrool_apps_contain
    if work_dir:
        for filename in os.listdir(work_dir):
            file_item = os.path.join(work_dir, filename)
            if os.path.isdir(file_item):
                app_list.append(file_item)

    return app_list
