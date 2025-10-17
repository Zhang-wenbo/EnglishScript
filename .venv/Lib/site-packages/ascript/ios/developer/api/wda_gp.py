import re

from ascript.ios.developer.api.dao import ImgInout
import requests
from ascript.ios.screen.gp import Point

host = "http://localhost:8100"
url_find_colors = f"{host}/screenshotFindColors"
url_counting_color = f"{host}/screenshotCountingColors"
url_screen_cache = f"{host}/screenshotCache"


def screen_cache(cache: bool):
    params = {
        'cache': cache,
    }
    response = requests.get(url_find_colors, params)
    response.raise_for_status()
    return True


def find_colors(img_inout: ImgInout, colors, space, ori, diff, num):
    rect_params = ""
    diff = (diff[0] << 16) | (diff[1] << 8) | diff[2]
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])
    params = {
        'maxPoints': num,
        'colors': colors,
        'diff': diff,
        'ori': ori,
        'space': space,
        'rect': rect_params,
    }
    response = requests.get(url_find_colors, params)
    response.raise_for_status()

    res = []

    for r in response.json()['value']:
        x = r['x']
        y = r['y']
        res.append(Point(x, y))

    return res


def counting_color(img_inout: ImgInout, colors, diff):
    rect_params = ""
    diff = (diff[0] << 16) | (diff[1] << 8) | diff[2]
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])

    params = {
        'colors': colors,
        'diff': diff,
        'rect': rect_params,
    }

    # print(params)

    response = requests.get(url_counting_color, params)
    response.raise_for_status()
    # print(response.json())
    return response.json()['value']


def ocr(mode: int, img_inout: ImgInout, threshold=0.2, pattern=None):
    rect_params = ""
    if img_inout.rect:
        rect_params = ','.join([str(num) for num in img_inout.rect])

    params = {
        'rect': rect_params,
    }

    response = requests.get(url_counting_color, params)
    response.raise_for_status()
    result = response.json()['value']
    res = []

    for r in result:
        x = r['x']
        y = r['y']
        w = r['w']
        h = r['h']
        txt = r['txt']
        c = r['confidence']
        center_x = x + w / 2
        center_y = y + h / 2
        match = True
        if pattern:
            if not re.search(pattern, txt):
                match = False

        if c >= threshold and match:
            res.append({
                "result": (center_x, center_y),
                "rect": (x, y, x + w, y + h),
                "center_x": center_x,
                "center_y": center_y,
                "confidence": c,
                "text": txt
            })

    return res
