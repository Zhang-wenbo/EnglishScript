print("阅读开始执行")
"""
我们不考虑正确性，全选D即可
"""
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
    read = {
        key: action.Point(value["x"], value["y"])
        for key, value in coordinates["read"].items()
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

# ----- 2.进入阅读主界面 -----#
time.sleep(1)
action.click(read["请点击阅读"]) # 点击语法选项卡
time.sleep(1)
action.click(read["请点击目标卡包"])  # 点击卡包
time.sleep(1)

# ----- 下滑最底并全点击D选项 ----- #
while True:
    # 检测确认按钮
    No = FindImages.find_template([R.img("确认.png")], confidence=0.9, rgb=True)
    if No:
        action.click(No["center_x"], No["center_y"])
        print("点击确认按钮")
        time.sleep(0.5)  # 稍微等一等界面更新

    # 下滑到底，确保D可见
    action.slide(
        read["请点击阅读"].x,
        read["请点击阅读"].y,
        read["请点击目标卡包"].x,
        read["请点击目标卡包"].y,
        20
    )
    time.sleep(0.5)

    # 检测D选项
    D = FindImages.find_sift([R.img("D.png")], confidence=0.9)
    if D:
        action.click(D["center_x"], D["center_y"])
        print("点击D选项")
        time.sleep(0.5)

        # 点击“下一个”
        action.click(read["请点击下一个"])
        print("点击下一个")
        time.sleep(0.5)
    else:
        # 若找不到D选项，也点击“下一个”，保证流程不阻塞
        action.click(read["请点击下一个"])
        print("未找到D选项，点击下一个")
        time.sleep(0.5)

    # 检测是否完成
    finish = FindImages.find_template([R.img("完成.png")], confidence=0.8, rgb=True)
    if finish:
        print("检测到完成按钮，退出阅读")
        action.Key.back()
        time.sleep(0.5)
        break

action.Key.back()
print("阅读结束")

