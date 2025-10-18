# 在主文件中只导包一次，其他文件就可以直接使用了
import json # JSON文件处理
from ascript.android.ui import WebWindow # 在Android上使用UI
from ascript.android.system import R # 路径信息


# 消息通道
def tunner(k, v):
    print(k, v)
    res = json.loads(v)
    for k, v in res.items():
        if k == "click_where" and v == "on":
            from . import click_where
            continue
        if k == "get_words_spell_coordinates" and v == "on":
            from . import get_words_spell_coordinates
            continue
        if k == "get_words_turn_coordinates" and v == "on":
            from . import get_words_turn_coordinates
            continue
        if k == "get_listen_coordinates" and v == "on":
            from . import get_listen_coordinates
            continue
        if k == "get_grammar_coordinates" and v == "on":
            from . import get_grammar_coordinates
            continue
        if k == "get_read_coordinates" and v == "on":
            from . import get_read_coordinates
            continue
        if k == "单词-拼写" and v == "on":
            from . import words_spell
            continue
        if k == "单词-翻转" and v == "on":
            from . import words_turn
            continue
        if k == "听力" and v == "on":
            from . import listen
            continue
        if k == "语法" and v == "on":
            from . import grammar
            continue
        if k == "阅读" and v == "on":
            from . import read
            continue
        break
    print("任务已结束")


w = WebWindow(R.ui("SettingUI.html"), tunner)
w.width(-1)
w.height("75vh")
w.show()
