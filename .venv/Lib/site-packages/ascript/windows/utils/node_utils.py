import win32gui


def get_all_window(model: int):
    win32gui.EnumWindows()
