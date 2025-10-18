# get_words_spell_coordinates.py
from ascript.android import action  # 行为操作库
import json  # JSON文件识别
from airscript.system import R  # 文件路径
import time  # 延时

# ----- 1. 导包 ----- #
import time
from ascript.android import action


# ----- 2. 定义获取点击坐标函数 ----- #
def get_click_coordinate(prompt, repeat_click=False):
    """
    获取点击坐标并执行点击操作
    repeat_click: 是否执行重复点击
    """
    coordinate = action.catch_click(prompt, False)  # 等待用户点击
    time.sleep(0.5)  # 延时，避免操作过快

    # 如果需要重复点击，则再次点击
    if repeat_click:
        time.sleep(0.5)
        action.click(coordinate, 20)

    # 返回点击坐标
    return {"x": coordinate.x, "y": coordinate.y}


# ----- 3. 定义提示词列表 ----- #
prompts = [
    "请点击单词", "请点击开始", "请点击确定",
    "请点击大小写转换键", "请点击删除键", "请点击确认键",
    "请点击卡片左上角", "请点击卡片右下角",
    "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
    "a", "s", "d", "f", "g", "h", "j", "k", "l",
    "z", "x", "c", "v", "b", "n", "m"
]

# ----- 4. 定义需要重复点击的提示词列表 ----- #
repeat_click_prompts = ["请点击单词", "请点击开始", "请点击确定"]

# ----- 5. 遍历执行任务 ----- #
words_spell = {}
for prompt in prompts:
    # 判断当前提示词是否需要重复点击
    is_repeat = prompt in repeat_click_prompts

    # 获取点击坐标（是否重复点击由 is_repeat 控制）
    coord = get_click_coordinate(prompt, repeat_click=is_repeat)

    # 保存结果：以提示词为键，坐标为值
    words_spell[prompt] = coord

# 从文件加载现有坐标信息
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    coordinates = {}

# 更新或添加单词拼写任务坐标
coordinates["words_spell"] = words_spell

# 保存到同一个文件
with open(R.sd("coordinates.json"), "w+") as f:  # 覆盖写模式
    json.dump(coordinates, f)

time.sleep(1)
action.Key.back()
time.sleep(0.5)
action.Key.back()

print("单词拼写坐标已保存到coordinates.json文件中")
