import os.path
from ctypes import Union

from ascript.android.system import R

from .gp import GPTask, Result
import numpy as np
import cv2
import random
from ascript.android.screen import ascv
from PIL import Image
from ascript.android import screen



class Crop(GPTask):
    name = "图片裁剪"
    ui_path = "/website/gpui/crop/"

    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        start_x, start_y = self.left, self.top
        width, height = self.right - self.left, self.bottom - self.top

        if self.right < self.left or self.bottom < self.top:
            raise ValueError("尺寸异常")

        # 使用NumPy数组切片进行裁剪
        cropped_image = cv_image[start_y:start_y + height, start_x:start_x + width]
        return Result(cropped_image, self.left + offset_x, self.top + offset_y, data)


class GrayImage(GPTask):
    name = "灰度图"
    ui_path = "/website/gpui/grayimage/"

    def __init__(self):
        pass

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        num_channels = cv_image.shape[2]
        if (num_channels == 3):
            gray_img = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        else:
            raise Exception("颜色通道错误")
        return Result(gray_img, offset_x, offset_y, data)


class Threshold(GPTask):
    name = "二值化"
    ui_path = "/website/gpui/threshold/"

    def __init__(self, threshold: int, inv: bool = False):
        self.threshold = threshold
        self.inv = inv

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:

        if len(cv_image.shape) != 2:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        method = cv2.THRESH_BINARY

        if self.inv:
            method = cv2.THRESH_BINARY_INV

        ret, thresholded_image = cv2.threshold(cv_image, self.threshold, 255, method)

        return Result(thresholded_image, offset_x, offset_y, data)


class Erode(GPTask):
    name = "腐蚀"
    ui_path = "/website/gpui/erode/"

    def __init__(self, kernel_size: int = 5, iterations: int = 1):
        self.kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.iterations = iterations

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        erode_img = cv2.erode(cv_image, self.kernel, iterations=self.iterations)
        return Result(erode_img, offset_x, offset_y, data)


class Dilate(GPTask):
    name = "膨胀"
    ui_path = "/website/gpui/dilate/"

    def __init__(self, kernel_size: int = 5, iterations: int = 1):
        self.kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.iterations = iterations

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        erode_img = cv2.dilate(cv_image, self.kernel, iterations=self.iterations)
        return Result(erode_img, offset_x, offset_y, data)


class MorphClose(GPTask):
    name = "闭运算"
    ui_path = "/website/gpui/morphclose/"

    def __init__(self, kernel_size: int = 5, iterations: int = 1):
        self.kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.iterations = iterations

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        closing = cv2.morphologyEx(cv_image, cv2.MORPH_CLOSE, self.kernel)
        return Result(closing, offset_x, offset_y, data)


class MorphOpen(GPTask):
    name = "开运算"
    ui_path = "/website/gpui/morphopen/"

    def __init__(self, kernel_size: int = 5, iterations: int = 1):
        self.kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.iterations = iterations

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        closing = cv2.morphologyEx(cv_image, cv2.MORPH_OPEN, self.kernel)
        return Result(closing, offset_x, offset_y, data)


class GaussianBlur(GPTask):
    name = "高斯模糊"
    ui_path = "/website/gpui/gaussianblur/"

    def __init__(self, ksize: int = 5, sigmaX: int = 0):
        self.kernel = (5, 5)
        self.sigmaX = sigmaX

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        blurred_image = cv2.GaussianBlur(cv_image, self.kernel, self.sigmaX)
        return Result(blurred_image, offset_x, offset_y, data)


class Canny(GPTask):
    name = "边缘检测"
    ui_path = "/website/gpui/canny/"
    RETR_TREE = cv2.RETR_TREE
    RETR_LIST = cv2.RETR_LIST
    RETR_EXTERNAL = cv2.RETR_EXTERNAL

    DRAW_NONE = 0
    DRAW_ALL = 1
    DRAW_RECT = 2
    DRAW_RECT_FILL = 3

    def __init__(self, low_threshold: int = 50, high_threshold: int = 150, mode: int = RETR_EXTERNAL,
                 draw: int = DRAW_ALL, desc: bool = False,
                 left_range: list = None, top_range: list = None,
                 width_range: list = None, height_range: list = None):
        self.low_t = low_threshold
        self.high_t = high_threshold
        self.mode = mode
        self.draw = draw
        self.left_range = left_range
        self.top_range = top_range
        self.width_range = width_range
        self.height_range = height_range
        self.desc = desc
        # print([self.left_range, self.top_range, self.width_range, self.height_range])

    @staticmethod
    def in_range(v, v_range: list, max_v):
        if not v_range:
            return True

        if len(v_range) == 1:
            v_range.append(max_v)

        if v_range[1] < 1:
            v_range[1] = max_v

        if v_range[0] <= v <= v_range[1]:
            return True

        return False

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        # erode_img = cv2.ca(cv_image, self.kernel, iterations=self.iterations)

        data = []

        height, width = cv_image.shape[:2]
        edges = cv2.Canny(cv_image, self.low_t, self.high_t)
        contours, _ = cv2.findContours(edges, self.mode, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            if not Canny.in_range(x, self.left_range, width):
                continue

            if not Canny.in_range(y, self.top_range, height):
                continue

            if not Canny.in_range(w, self.width_range, width):
                continue

            if not Canny.in_range(w, self.height_range, width):
                continue

            if self.draw == Canny.DRAW_ALL:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.drawContours(cv_image, [cnt], -1, color=color, thickness=2)
            elif self.draw == Canny.DRAW_RECT:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), color, 2)
            elif self.draw == Canny.DRAW_RECT_FILL:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (255, 255, 255), -1)
            # 获取边界框

            if self.desc:
                draw_text = f"xy:({x},{y}) wh:({w},{h})"
                cv2.putText(cv_image, draw_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2,
                            lineType=cv2.LINE_AA)

            data.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h
            })

        return Result(cv_image, offset_x, offset_y, data)


class CvFontLib(GPTask):
    name = "图片字库"
    ui_path = "/website/gpui/cvfontlib/"

    def __init__(self, part_img: list, font_lib: list, confidence: int = 0.95, rect: list = None, spacing: int = 5,
                 rgb: bool = False):
        self.part_img = part_img
        self.font_lib = font_lib
        self.spacing = spacing
        self.confidence = confidence
        self.rect = rect
        self.rgb = rgb

    @staticmethod
    def sort_and_concatenate_chars(data):
        # print(data)

        # 提取所有字符的矩形框左边界和字符本身

        # print(data)

        chars_with_left_edge = [(char['rectangle'][0][0],
                                 (char['rectangle'][0][1] + (char['rectangle'][1][1] - char['rectangle'][0][1]) / 2),
                                 char['font']) for sublist in data for char in sublist]

        # print("????", chars_with_left_edge)

        # 根据左边界进行排序
        # sorted_chars = sorted(chars_with_left_edge, key=lambda x: (x[1], x[0]))

        # print(chars_with_left_edge)

        def bucketize_y(y, bucket_size=10):
            # 将y坐标分配到桶中，桶的大小为bucket_size
            return y // bucket_size * bucket_size

        # [(184, 339.5, '/'), (185, 337.5, '/'), (183, 341.5, '/')]

        # 排序键是一个元组：(y的桶值, x坐标)
        sorted_chars = sorted(chars_with_left_edge, key=lambda x: (bucketize_y(x[1]), x[0]))

        # 拼接font字段
        concatenated_font = ''.join(item[2] for item in sorted_chars)

        # print(concatenated_font, "??????")

        return concatenated_font

    @staticmethod
    def group_chars_by_distance(data, threshold=10):
        # 提取所有字符的矩形框左边界和字符本身，并排序
        left_edges = sorted([(char['rectangle'][0][0], char['font']) for sublist in data for char in sublist])

        # 初始化结果列表和当前词组的起始左边界
        grouped_chars = []
        current_word = ''
        current_word_start_edge = None

        # 遍历排序后的左边界和字符
        for left_edge, char in left_edges:
            # 如果当前词组为空或当前字符与前一个字符的间距小于阈值
            if not current_word or (
                    current_word_start_edge is not None and left_edge - current_word_start_edge < threshold):
                # 添加字符到当前词组
                current_word += char
            else:
                # 如果间距大于或等于阈值，则将当前词组添加到结果列表中，并开始新的词组
                grouped_chars.append((current_word_start_edge, current_word))
                current_word = char
                current_word_start_edge = left_edge

                # 添加最后一个词组（如果有的话）
        if current_word:
            grouped_chars.append((current_word_start_edge, current_word))

        return grouped_chars

    def sort_group(self, data):
        # print('????-----s-', data)
        chars_with_left_edge = [(char['rectangle'][0][0],
                                 (char['rectangle'][0][1] + (char['rectangle'][1][1] - char['rectangle'][0][1]) / 2),
                                 char['font']) for sublist in data for char in sublist]

        # print("??????----", chars_with_left_edge)
        groups = []
        for c in chars_with_left_edge:
            center_y = c[1]
            match = False
            for i, g in enumerate(groups):
                if len(g) > 0 and abs(g[0][1] - center_y) < self.spacing:
                    groups[i].append(c)
                    match = True
                    break

            if not match:
                groups.append([c])

        groups.sort(key=lambda x: x[0][1])

        group_text = []
        for g in groups:
            g.sort(key=lambda x: x[0])
            temp_g = [tup[2] for tup in g]
            group_text.append(''.join(temp_g))

        concatenated_font = [item for sublist in groups for item in sublist]

        third_elements = [tup[2] for tup in concatenated_font]

        # 使用 join() 方法将提取出的元素拼接成一个字符串
        result_string = ''.join(third_elements)

        return result_string, concatenated_font, group_text

    def run(self, cv_image: np.ndarray, offset_x: int = 0, offset_y: int = 0, data=None) -> Result:
        words = []
        index = -1

        if self.rect:
            x, y, r, b = self.rect
            cv_image = cv_image[y:b, x:r]

        image_copy = cv_image.copy()

        for img in self.part_img:
            index = index + 1
            res = ascv.find_all_template(image_copy, img, rect=self.rect, threshold=self.confidence, rgb=self.rgb)
            for r in res:
                r["font"] = self.font_lib[index]
                # 回填图片,不让
                x, y = r["rectangle"][0]
                r, b = r["rectangle"][3]
                # image = Image.fromarray(image_copy)
                # print(x, y, r, b)

                off_x = 0
                off_y = 0
                if self.rect:
                    off_x = self.rect[0]
                    off_y = self.rect[1]

                cv2.rectangle(image_copy, (x - off_x, y - off_y), (r - off_x, b - off_y), (0, 0, 0), -1)  # -1 表示填充整个矩形

            words.append(res)
        res, all_words, groups = self.sort_group(words)
        # res = CvFontLib.sort_and_concatenate_chars(words)

        # image_save = Image.fromarray(image_copy)
        # image_save.save("sdcard/1/4.png")

        data = {
            "text": res,
            "words": words,
            "group": groups
        }

        if res == "":
            data = None

        return Result(cv_image, offset_x, offset_y, data)



