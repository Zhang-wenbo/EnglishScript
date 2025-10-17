# get_listen_coordinates.py
from ascript.android import action  # 行为操作库
import json  # JSON文件识别
from airscript.system import R  # 文件路径
import time  # 延时

# 获取点击坐标并执行点击操作
def get_click_coordinate(prompt):
    """获取点击坐标并执行点击操作"""
    coordinate = action.catch_click(prompt, False)
    time.sleep(0.5)  # 延时，避免操作过快
    action.click(coordinate, 20)  # 执行点击操作
    return {"x": coordinate.x, "y": coordinate.y}

# ----- 1.获取听力任务坐标 ----- #
prompts = ["请点击听力", "请点击目标卡包", "请点击确认", "请点击播放", "请点击下一个"]
listen = [get_click_coordinate(prompt) for prompt in prompts]  # 获取所有坐标并保存

# 从文件加载现有坐标信息
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    coordinates = {}

# 更新或添加听力任务坐标
coordinates["listen"] = listen

# 保存到同一个文件
with open(R.sd("coordinates.json"), "w+") as f:  # 覆盖写模式
    json.dump(coordinates, f)

time.sleep(1)
action.Key.back()
time.sleep(0.5)
action.Key.back()

print("听力坐标已保存到 coordinates.json 文件中")