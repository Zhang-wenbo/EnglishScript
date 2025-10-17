print("语法开始执行")
# ----- 1.导库导包 ----- #
from ascript.android.screen import FindImages # 找图
from ascript.android.screen.gp_tool import R # 路径检索
from ascript.android import action # 行为控制
import json # JSON文件识别
import time # 延时

# 从click_where.json文件加载必要坐标信息
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
    # 将加载的字典转换回 Point 对象
    grammar = [action.Point(pt["x"], pt["y"]) for pt in coordinates["grammar"]]
except FileNotFoundError:
    print("错误：未找到click_where.json文件，请先运行坐标获取程序。")
    exit(1)
except json.JSONDecodeError:
    print("错误：click_where.json文件格式不正确。")
    exit(1)
except KeyError:
    print("错误：click_where.json文件中缺少必要的坐标信息。")
    exit(1)

# ----- 2.进入语法主界面 -----#
time.sleep(1)
action.click(grammar[0]) # 点击语法选项卡
time.sleep(1)
action.click(grammar[1])  # 点击卡包
time.sleep(1)

"""
语法有两种情况，一种直接下一个就行，另一种是全点击A选项
"""

# 第一种情况-直接全下一个
while True:
    action.click(grammar[2])
    time.sleep(0.5)

    # 检测是否完成
    finish = FindImages.find_template([R.img("完成.png")], confidence=0.8, rgb=True)
    if finish:
        action.Key.back()
        time.sleep(0.5)
        break

# # 第2种情况-全点击A选项
# while True:
#     A = FindImages.find_template([R.img("A.png")])
#     action.click(A["center_x"], A["center_y"])
#     time.sleep(1)
#     action.click(go_next["center_x"], go_next["center_y"])
#     time.sleep(1)
#     finish = FindImages.find_template([R.img("完成.png"), ], confidence=0.95, rgb=True)
#     if finish:
#         action.Key.back()
#         time.sleep(1)
#         break

action.Key.back()
print("语法结束")

