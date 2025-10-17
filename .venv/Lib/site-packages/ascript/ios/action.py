from typing import Union


def click(x: int, y: int = None, dur: int = 20):
    if type(x) == float:
        x = int(x)

    if type(y) == float:
        y = int(y)

    if type(x) == int:
        asclick(x, y, dur)
    else:
        asclick(x, dur)
