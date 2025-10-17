import pyautogui
import pyperclip

LEFT = "left"
MIDDLE = "middle"
RIGHT = "right"
PRIMARY = "primary"
SECONDARY = "secondary"


def click(x=None, y=None, clicks=1, interval=0.0, button=PRIMARY, duration=0.02, tween=pyautogui.linear,
          logScreenshot=None, _pause=True):
    pyautogui.click(x, y, clicks, interval, button, duration, tween, logScreenshot, _pause)


def scroll(lines: int, x: int = None, y: int = None, h: bool = False, v: bool = True):
    if x and y:
        pyautogui.moveTo(x, y)

    if h:
        pyautogui.hscroll(lines, x, y)
    elif v:
        pyautogui.vscroll(lines, x, y)
    else:
        pyautogui.scroll(lines, x, y)


def drag(start_x: int, start_y: int, to_x: int, to_y: int, duration: float = 0.5):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(to_x, to_y, duration)


def mouse_down(x: int, y: int, button: str = PRIMARY, duration: float = 0.5, tween=pyautogui.linear):
    pyautogui.mouseDown(x, y, button, duration, tween)


def mouse_move(x: int, y: int, duration: float = 0.5, tween=pyautogui.linear):
    pyautogui.moveTo(x, y, duration, tween)


def mouse_up(x: int, y: int, button: str = PRIMARY, duration: float = 0.5, tween=pyautogui.linear):
    pyautogui.mouseUp(x, y, button, duration, tween)


def input(msg: str, interval=0.0):
    if any(0x7F < ord(c) < 0x10000 for c in msg):
        # 包含中文
        pyperclip.copy(msg)
        pyautogui.hotkey('ctrl', 'v')
    else:
        pyautogui.typewrite(msg, interval)


def key(keys, presses=1, interval=0.0):
    pyautogui.press(keys, presses, interval)


def key_hot(*args, **kwargs):
    pyautogui.hotkey(args, kwargs)


def key_down(key: str):
    pyautogui.keyDown(key)


def key_up(key:str):
    pyautogui.keyUp(key)
