print("听力开始执行")

# ----- 1.导库导包 ----- #
from ascript.android.screen import FindImages  # 图色识别->找图
from ascript.android.system import R  # 路径找文件
from ascript.android import action  # 行为操作
import time  # 时间延时
import json  # json文件处理

# 从click_where.json文件加载必要坐标信息
try:
    with open(R.sd("coordinates.json"), "r") as f:
        coordinates = json.load(f)
    # 将加载的字典转换回 Point 对象
    listen = [action.Point(pt["x"], pt["y"]) for pt in coordinates["listen"]]
except FileNotFoundError:
    print("错误：未找到click_where.json文件，请先运行坐标获取程序。")
    exit(1)
except json.JSONDecodeError:
    print("错误：click_where.json文件格式不正确。")
    exit(1)
except KeyError:
    print("错误：click_where.json文件中缺少必要的坐标信息。")
    exit(1)

# ----- 2.进入听力主界面 -----#
time.sleep(1)
action.click(listen[0])  # 点击听力选项卡
time.sleep(1)
action.click(listen[1])  # 点击卡包
time.sleep(1)
action.click(listen[2])  # 点击确认
time.sleep(1)

# ----- 3.执行第一个播放 -----#
action.click(listen[3])

# ----- 4.循环执行 -----#
while True:
    # 检查绿色麦克风
    voice = FindImages.find_template([R.img("绿色麦克风.png")], confidence=0.95, rgb=True)
    if voice:
        # 如果检测到绿色麦克风，点击“下一个”按钮
        action.click(listen[4])  # 通过 list 中的坐标点击“下一个”
        print("检测到绿色麦克风，并点击下一个")
        time.sleep(0.5)  # 给适应时间跳转到下一个听力
        action.click(listen[3])  # 再次点击播放按钮
        print("点击播放按钮")
        time.sleep(0.5)  # 适当延时，确保操作被执行
    else:
        time.sleep(0.5)  # 适当延时在播放时检测麦克风的频率，避免高频检测占用资源

    # 检测是否完成
    finish = FindImages.find_template([R.img("完成.png")], confidence=0.8, rgb=True)
    if finish:
        action.Key.back()
        time.sleep(0.5)
        break

action.Key.back()  # 最终返回到菜单主页面
print("听力任务结束")
