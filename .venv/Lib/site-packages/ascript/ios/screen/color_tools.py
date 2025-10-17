import json
import time
import numpy as np
from PIL import Image
from ascript.ios.screen.gp import Point


class ColorPoint:
    def __init__(self, x, y, rgb=None, diff=None):
        self.x = x
        self.y = y
        self.rgb = rgb
        self.diff = diff

    def __repr__(self):
        return json.dumps({
            "x": self.x,
            "y": self.y,
            "rgb": self.rgb,
        })

    def __sub__(self, other):
        self.x = self.x - other.x
        self.y = self.y - other.y
        return self


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    length = len(hex_color)
    if length != 6:
        raise ValueError("Invalid hex color code '{}'".format(hex_color))
    r = int(hex_color[:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:], 16)
    return [r, g, b]


def ana_colors_r(colors_str: str):
    # 拆分颜色
    colors = []
    index = 0
    for color_str in colors_str.split('|'):
        # 将 RGB 颜色值转换为整数数组
        c_s = color_str.split(',')

        color = c_s[2]
        diff = None
        if '-' in color:
            color, diff = color.split('-')
            if diff:
                diff = hex_to_rgb(diff)

        if index == 0:
            colors.append(ColorPoint(int(c_s[0]), int(c_s[1]), hex_to_rgb(color), diff))
        else:
            colors.append(ColorPoint(int(c_s[0]), int(c_s[1]), hex_to_rgb(color), diff) - colors[0])

        index = index + 1

    return colors


def ana_colors(colors_str: str):
    # 拆分颜色
    colors = []
    index = 0
    for color_str in colors_str.split('|'):
        # 将 RGB 颜色值转换为整数数组
        c_s = color_str.split(',')

        color = c_s[2]
        diff = None
        if '-' in color:
            color, diff = color.split('-')
            if diff:
                diff = hex_to_rgb(diff)

        colors.append(ColorPoint(int(c_s[0]), int(c_s[1]), hex_to_rgb(color), diff))

        index = index + 1

    return colors


def ana_single_scolors(colors_str: str):
    colors = []
    index = 0
    for color_str in colors_str.split('|'):
        # 将 RGB 颜色值转换为整数数组
        color = color_str
        diff = None
        if '-' in color:
            color, diff = color.split('-')
            if diff:
                diff = hex_to_rgb(diff)

        colors.append(ColorPoint(0, 0, hex_to_rgb(color), diff))

        index = index + 1

    return colors


def compare_color(color1, color2, diff):
    for i in range(2):
        if abs(color1[i].astype(np.int32) - color2[i]) > diff[i]:
            return False
    return True


def compare_color_n(color1, color2, diff):
    for i in range(2):
        if abs(color1[i] - color2[i]) > diff[i]:
            return False
    return True


def check_color(colors, y, x, h, w, diff, image: np.ndarray):
    color = colors[0]
    if compare_color(image[y, x], color.rgb, diff if color.diff is None else color.diff):
        for i in range(1, len(colors)):
            color = colors[i]
            ny = color.y + y
            nx = color.x + x
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                return False
            if not compare_color(image[ny, nx], color.rgb, diff if color.diff is None else color.diff):
                return False
        return True
    return False


def check_space(y, x, space_blocks):
    for block in space_blocks:
        if block[0] < y < block[1] and block[2] < x < block[3]:
            return False

    return True


def find_colors(colors: str, rect: tuple = None, space: int = 5, ori: int = 2, diff: list = (5, 5, 5), num=-1,
                image: Image.Image = None):
    colors = ana_colors_r(colors)

    image = np.array(image)
    rows, cols, _ = image.shape
    if ori == 1:
        pass
    points = []
    points_block = []

    if rect is None:
        rect = [0, 0, cols, rows]
    print("start", time.time())

    # 这里是根据不通的方向遍历图片 ,默认是2

    if ori == 1:
        for x in range(rect[0], rect[2]):
            for y in range(rect[1], rect[3]):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 2:
        # 双层循环,遍历图像的没一个像素
        for y in range(rect[1], rect[3]):
            for x in range(rect[0], rect[2]):
                # 检测当前 坐标 是否 在已存在点的范围之内. 如果存在放弃. 如果不存在继续
                # 检测 颜色当前点颜色规则是否符合.
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 3:
        for y in range(rect[1], rect[3]):
            for x in range(rect[2] - 1, rect[0], -1):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 4:
        for x in range(rect[2] - 1, rect[0], -1):
            for y in range(rect[1], rect[3]):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 5:
        for x in range(rect[2] - 1, rect[0], -1):
            for y in range(rect[3] - 1, rect[1], -1):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 6:
        for y in range(rect[3] - 1, rect[1], -1):
            for x in range(rect[2] - 1, rect[0], -1):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    elif ori == 7:
        for y in range(rect[3] - 1, rect[1], -1):
            for x in range(rect[0], rect[2]):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))

    elif ori == 8:
        for x in range(rect[0], rect[2]):
            for y in range(rect[3] - 1, rect[1], -1):
                if check_space(y, x, points_block) and check_color(colors, y, x, rows, cols, diff, image):
                    points.append(Point(x, y))
                    if num != -1 and len(points) >= num:
                        return points
                    points_block.append((y - space, y + space, x - space, x + space))
    # if ori == 2:

    print("end", time.time())

    return points
