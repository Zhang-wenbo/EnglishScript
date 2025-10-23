"""
1.进入翻转主页面
2.几个函数
【学习卡执行函数 -> 选择卡执行函数 -> 确定是学习卡还是选择卡并跳转到对应函数】
【"完成.png"和"确认.png"的点击函数】
"""

print("单词翻转任务开始执行")


# ----- 1.相关库、包、文件的引入 ----- #
import time, json, re, difflib
from ascript.android import action
from ascript.android.system import R
from android.view.animation import AccelerateInterpolator # 差速器-加速
from ascript.android.system import R
from ascript.android.screen import FindImages
from ascript.android import plug
plug.load("TomatoOcr:1.1.7")
from TomatoOcr import TomatoOcr
plug.load("esp32") # ESP32开发板
from esp32 import UsbDevice # Usb模型
usb = UsbDevice() # 自动扫描AS设备并连接

with open(R.sd("coordinates.json"), "r", encoding="utf-8") as f:
    coordinates = json.load(f)
words_turn = {
    key: action.Point(value["x"], value["y"])
    for key, value in coordinates["words_turn"].items()
}


# ----- 2.必要全局变量的配置 ----- #
KEY = '2LVXTSTBSMYLBJDURSL5NEOXZRE1P2I4|DltTFFN0OAKhNaY6FXgLK5BI'
AREA = [
    words_turn["请点击卡片左上角"].x, words_turn["请点击卡片左上角"].y,
    words_turn["请点击卡片右下角"].x, words_turn["请点击卡片右下角"].y
]
KEY_WORD = re.compile(r"^[A-Za-z]+$")  # 检测纯粹单词部分
POS_PATTERN = re.compile(r"[\u4e00-\u9fa5]+")  # 检测词性-Unicode编码中文
OPTION_PATTERN = re.compile(r"^([A-D])[\.．、\s]+(.*)$")  # 检测选项部分

DICT = {}

# ----- 3.核心函数 ----- #


# 使检测的字符串仅保留中文
def filter_chinese(s):
    return ''.join(re.findall(r'[\u4e00-\u9fa5]', s))


# 返回两字符串的相似度
def get_similarity(str1: str, str2: str) -> float:
    value = difflib.SequenceMatcher(None, str1, str2).ratio()
    return value


"""
learn_card函数无需传参，根据指定矩形范围内进行OCR识别，
返回{单词:释义}的字典，其存再总字典DICT中
其中因OCR的原因，若释义为多行，它就会分开，
这里当检测到第一行释义就break掉，防止值被改变
"""


def learn_card(max_try=3):
    for try_num in range(max_try):
        key = None
        meaning_list = []
        res = TomatoOcr.find_all(
            mode="dev", http_interval_time=43200, license=KEY, rec_type="ch-3.0",
            box_type="rect", ratio=1.9, threshold=0.8, return_type="json", capture=AREA,
        )
        try:
            res = json.loads(res)
        except Exception as e:
            print(f"OCR JSON error: {e}")
            continue
        for r in res:
            if KEY_WORD.match(r["words"]):
                key = r["words"].strip()
                print("单词为：" + key)
            if POS_PATTERN.search(r["words"]):
                value = filter_chinese(r["words"]).strip()
                print("释义为：" + value)
                meaning_list.append(value)
        if key and meaning_list:
            meaning_full = ''.join(meaning_list)
            DICT[key] = meaning_full
            return DICT
        print(f"OCR未能识别到有效单词或释义，第{try_num+1}次重试，尝试自动点击翻转卡片并处理弹窗")
        # 未找到，直接进行点击翻转和弹窗处理
        center_x = (words_turn["请点击卡片左上角"].x + words_turn["请点击卡片右下角"].x) // 2
        center_y = (words_turn["请点击卡片左上角"].y + words_turn["请点击卡片右下角"].y) // 2
        usb.click(center_x, center_y, 20)
        png()  # 尝试关闭/确认弹窗
    print("多次未能识别成功，结束本次学习卡处理。")
    return None


"""
scelect_card函数无需传参也无返回值，它对存在于字典中的单词自动点击其释义位置
"""


def select_card(threshold=0.5):
    res = TomatoOcr.find_all(
        mode="dev", http_interval_time=43200, license=KEY, rec_type="ch-3.0",
        box_type="rect", ratio=1.9, threshold=0.8, return_type="json", capture=AREA,
    )
    try:
        res = json.loads(res)
    except Exception as e:
        print(f"OCR JSON error: {e}")
        png() # 异常自动弹窗
        return None
    print("识别结果为：", res)
    print("现存字典为：", DICT)
    matched = False
    key_word = None
    for r in res:
        word = KEY_WORD.match(r["words"])
        explanation = filter_chinese(r["words"])
        if word:
            key_word = word.group().strip()
            print("单词为：", key_word)
            continue
        if key_word in DICT:
            meanings = DICT[key_word] # 这个变量指的是学习卡时得到的单词释义
            print("字符串A为:{},字符串B为{},其相似度为{}".format(explanation, meanings, get_similarity(explanation, meanings)))
            if get_similarity(explanation, meanings) >= threshold:
                location = r["location"]
                x_center = sum([p[0] for p in location]) // len(location)
                y_center = sum([p[1] for p in location]) // len(location)
                print("点击位置为：", x_center, y_center)
                usb.click(x_center + words_turn["请点击卡片左上角"].x, y_center + words_turn["请点击卡片左上角"].y, 20)
                print("已点击正确答案！")
                matched = True
                break
            else:
                print(f"OCR识别的选项词 {r['words']} 与释义未达到阈值{threshold}")
    if not matched:
        print("未成功匹配到释义，返回None，由主流程决定处理方式。")
        png()  # 失败自动尝试关闭弹窗
        return None
    return 0


"""
对页面卡包进行分类，识别学习卡和选择卡以进入不同函数
"""


def category():
    res = TomatoOcr.find_all(
        mode="dev", http_interval_time=43200, license=KEY, rec_type="ch-3.0",
        box_type="rect", ratio=1.9, threshold=0.8, return_type="json", capture=AREA,
    )
    res = json.loads(res)
    length = len(res)
    if length < 5:
        return learn_card()
    else:
        return select_card()


def png():
    yes = FindImages.find_template([R.img("确定.png")], confidence=0.8, rgb=True)
    done = FindImages.find_template([R.img("完成.png")], confidence=0.8, rgb=True)
    cont = FindImages.find_template([R.img("继续.png")], confidence=0.8, rgb=True)
    clicked = False
    if yes:
        print("检测到确认按钮并尝试点击")
        usb.click(yes["center_x"], yes["center_y"])
        clicked = True
    if cont:
        print("检测到继续按钮并尝试点击(强化训练)")
        usb.click(cont["center_x"], cont["center_y"])
        clicked = True
    if done:
        print("检测到完成按钮并尝试点击退出")
        usb.click(done["center_x"], done["center_y"]) # 点击完成后返回到两卡包位置，不能直接用back函数，因为会返回多级
        usb.click(words_turn["请点击左上角返回键"].x, words_turn["请点击左上角返回键"].y, 20)
        clicked = True
    return clicked


def main():
    while True:
        usb.click(words_turn["请点击卡片左上角"].x, words_turn["请点击卡片左上角"].y, 20)
        png()
        category()
        png()
        usb.slide(words_turn["请点击卡片右下角"].x, words_turn["请点击卡片右下角"].y,
                  words_turn["请点击卡片左上角"].x, words_turn["请点击卡片左上角"].y, 100)
        png()


# ----- 4.主程序 ----- #
action.click(words_turn["请点击单词"].x, words_turn["请点击单词"].y, 20)
time.sleep(0.5)

# 支持多卡包灵活扩展, 直接增加即可(在保证json文件中存在目标卡包坐标的情况下)
package_keys = [
    "请点击卡包(一)",
    "请点击卡包(二)"
]

while True:
    for pkg in package_keys:
        print(f"开始处理：{pkg}")
        action.click(words_turn[pkg].x, words_turn[pkg].y, 20)
        time.sleep(1.5)
        main()  # 卡包内部循环流程



