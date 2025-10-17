import time

from airscript.action import hidboard


def send_hex(hex_str: str):
    # print(hex_str)
    res = hidboard.send_hex(hex_str)
    if res == -2:
        print("没有检测到HID芯片")

    return res


def is_active():
    return hidboard.is_active()

# def set_screen_size(width: int, height: int):
#     formatted_string = f"00{width:04X}{height:04X}0000"
#     send_hex(formatted_string)
#
#
# def click(x: int, y: int, dur=20, key: int = 1):
#     down_hex = f"01{x:04X}{y:04X}0{int(key)}00"
#     send_hex(down_hex)
#     time.sleep(dur / 1000)
#     up_hex = f"01{x:04X}{y:04X}0000"
#     send_hex(up_hex)
#
#
# def slide(x, y, x1, y1, dur=20):
#     pass
