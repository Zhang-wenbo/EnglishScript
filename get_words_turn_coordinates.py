# get_words_turn_coordinates.py
from ascript.android import action  # 行为操作库
import json  # JSON文件识别
from airscript.system import R  # 文件路径
import time  # 延时


# ----- 2. 定义获取点击坐标函数 ----- #
def get_click_coordinate(prompt, repeat_click=False):
    """
    获取点击坐标并执行点击操作
    repeat_click: 是否重复点击
    """
    coordinate = action.catch_click(prompt, False)  # 等待用户点击
    time.sleep(0.5)  # 延时，避免操作过快

    # 如果需要重复点击，则再点击一次
    if repeat_click:
        time.sleep(0.5)
        action.click(coordinate, 20)

    # 返回坐标
    return {"x": coordinate.x, "y": coordinate.y}


# ----- 3. 定义提示词列表 ----- #
prompts = ["请点击单词", "请点击左上角返回键", "请点击卡包(一)", "请点击卡包(二)", "请点击卡片左上角", "请点击卡片右下角"]

# ----- 4. 定义需要重复点击的提示词列表 ----- #
repeat_click_prompts = ["请点击单词", "请点击卡包(二)"]

# ----- 5. 遍历执行任务 ----- #
words_turn = {}
for prompt in prompts:
    # 判断当前提示词是否在重复点击列表中
    is_repeat = prompt in repeat_click_prompts

    # 获取坐标（根据 is_repeat 判断是否重复点击）
    coord = get_click_coordinate(prompt, repeat_click=is_repeat)

    # 保存坐标结果
    words_turn[prompt] = coord

# 从文件加载现有坐标信息
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    coordinates = {}

# 更新或添加单词翻转任务坐标
coordinates["words_turn"] = words_turn

# 保存到同一个文件
with open(R.sd("coordinates.json"), "w+") as f:  # 覆盖写模式
    json.dump(coordinates, f)

time.sleep(1)
action.Key.back()
time.sleep(1)
action.Key.back()

print("单词翻转坐标已保存到coordinates.json文件中")
