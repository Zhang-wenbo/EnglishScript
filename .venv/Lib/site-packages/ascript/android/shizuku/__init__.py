from typing import Union

from airscript.system import SzkAgent


def shell(command: Union[str, list]):
    if type(command) == str:
        return SzkAgent.shell(command)
    else:
        return SzkAgent.shell_array(command)


def click(x: int, y: int):
    return shell(f"input tap {x} {y}")


def swipe(x1: int, y1: int, x2: int, y2: int, dur: int = 200):
    return shell(f"input swipe {x1} {y1} {x2} {y2} {dur}")
