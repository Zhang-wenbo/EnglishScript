print("单词拼写开始执行")

# ----- 1.导包导库 ----- #
from ascript.android import action  # 行为库
from ascript.android.screen import re  # 正则
from ascript.android.screen import json # JSON文件处理
from ascript.android.system import R  # 路径
from ascript.android.screen import FindImages  # 找图
from ascript.android import screen  # 屏幕信息
from ascript.android import plug  # 调插件
plug.load("TomatoOcr:1.1.7")  # 番茄OCR
from TomatoOcr import TomatoOcr
import time  # 延时
plug.load("esp32") # ESP32开发板
from esp32 import UsbDevice # Usb模型
usb = UsbDevice() # 自动扫描AS设备并连接

# ----- 2.加载坐标信息 ----- #
"""
coordinates.json存在于我们有权限的"/sd"卡路径下,
写入时都是通过gey-xx-coordinates项目完成的。
这个json读入后我们通过words_spell作为命名变量
"""
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
    # 将加载的字典转换回 Point 对象，若想返回元组，就去掉action.Point
    words_spell = {
        key: action.Point(value["x"], value["y"])
        for key, value in coordinates["words_spell"].items()
    }
except FileNotFoundError:
    print("错误：未找到click_where.json文件，请先运行坐标获取程序。")
    exit(1)
except json.JSONDecodeError:
    print("错误：click_where.json文件格式不正确。")
    exit(1)
except KeyError:
    print("错误：click_where.json文件中缺少必要的坐标信息。")
    exit(1)

# ----- 3.进入单词拼写主界面 -----#
usb.click(words_spell["请点击单词"].x, words_spell["请点击单词"].y, 20)  # 点击单词选项卡
time.sleep(1)
usb.click(words_spell["请点击开始"].x, words_spell["请点击开始"].y, 20)  # 点击拼写开始按钮
time.sleep(1)
usb.click(words_spell["请点击确定"].x, words_spell["请点击确定"].y, 20)  # 点击确定按钮
time.sleep(1)

# ----- 4.找正确单词函数 ----- #
"""
一直点击键盘上的q键20次后点击确认寻找正确答案
action.click函数(坐标,点击持续时长)
键盘上面是在触摸时才会输入，并且长按不会重复打字
"""
def find():
    for _ in range(20):
        usb.click(words_spell["q"].x, words_spell["q"].y, 20)  # 连续点击键盘q
    time.sleep(0.5)
    usb.click(words_spell["请点击确认键"].x, words_spell["请点击确认键"].y, 20)  # 点击确认按钮

    time.sleep(1) # 等待1s以确保提示成功显示

    result = TomatoOcr.find_all(
        mode="dev",
        http_interval_time=43200,  # 12h进行一次授权验证
        license="2LVXTSTBSMYLBJDURSL5NEOXZRE1P2I4|DltTFFN0OAKhNaY6FXgLK5BI",
        rec_type="ch-3.0",
        box_type="rect",
        ratio=1.6,
        threshold=0.8,
        return_type="json",
        binary=0,
        run_mode="slow",
        bg_color="white",
        ocr_type=3,
        capture=[
            words_spell["请点击卡片左上角"].x,
            words_spell["请点击卡片左上角"].y,
            words_spell["请点击卡片右下角"].x,
            words_spell["请点击卡片右下角"].y
        ]
    )
    print("TomatoOcr返回结果为:", result)
    # 将TomatoOcr返回的字符串转为Json格式
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            print("JSON 解析失败，请检查字符串格式。")
            result = []

    word = None  # 存放提取的英文单词

    # 处理OCR结果，提取单词
    for item in result:
        text = item["words"]
        if "提示" in text:
            # 去掉空格，防止OCR出现 "po ssibility" 等问题
            clean_text = text.replace(" ", "")
            # 用正则匹配提示后面的连续英文字母
            match = re.search(r"提示([A-Za-z]+)", clean_text)
            if match:
                word = match.group(1)
                break  # 找到就退出循环

    if word:  # 如果找到了单词，就返回
        print("提取结果为:", word)
        return word
    else:
        print("未找到单词，将尝试继续返回find函数查找...")
        # 检测完成标识
        finish = FindImages.find_template([R.img("完成.png")], confidence=0.8, rgb=True)
        if finish:
            print("检测到完成，提前终止拼写流程。")
            return None
        time.sleep(1)
        return find()  # 递归调用 find，直到找到为止

# ----- 5.拼写单词函数 ----- #
def spell(word):
    for i in word:
        if i.islower():  # 针对小写输入
            time.sleep(0.1)
            usb.click(words_spell[i].x, words_spell[i].y, 20)
        else:  # 针对大写输入
            usb.click(words_spell["请点击大小写转换键"].x, words_spell["请点击大小写转换键"].y, 20)
            usb.click(words_spell[i.lower()], 20)
            usb.click(words_spell["请点击大小写转换键"].x, words_spell["请点击大小写转换键"].y, 20)
    usb.click(words_spell["请点击确认键"].x, words_spell["请点击确认键"].y, 20)

# ----- 6.主程序函数 ----- #
def main():
    word = find()  # 一直找,直到返回一个单词或None
    if not word:
        return  # 直接返回，不再拼写
    usb.click(words_spell["请点击删除键"].x, words_spell["请点击删除键"].y, 20)  # 当错误满时,只需删除一次即可全部消除
    spell(word)  # 拼写这个单词

# -----7.主循环 ----- #
while True:
    main()
    # 检测是否完成
    finish = FindImages.find_template([R.img("完成.png"), ], confidence=0.8, rgb=True)
    if finish:
        print("检测到完成按钮，将尝试点击")
        usb.click(finish["center_x"], finish["center_y"]) # 该返回到卡包与拼写共存页面了
        time.sleep(1)
        action.Key.back() # 返回至主页面
        break

print("单词拼写结束")
