# EnglishScript
# 一、简介

天下苦英语久矣！我一直在寻找网上是否有大佬完成过翻转外语小程序脚本的开发，着实找到几个，但都对使用的操作描述的不够详细，也未能达到我心中的优秀水平。

于是，EnglishScript 应运而生，该程序无需电脑，仅需一块开发板外加手机，即可运行，方便快捷。

并且基于Layui制作了漂亮的任务设置页面，其坐标获取功能可用于不同分辨率手机的适配。

<img src="https://cdn.nlark.com/yuque/0/2025/jpeg/42519851/1760678331766-d5f7e8f6-2bf0-4afe-afda-c7d0a8d0f1d3.jpeg" alt="程序任务设置页面" height="300">

## 1.主功能脚本
* `listen.py`：听力
* `read.py`：阅读理解
* `grammar.py`：语法练习
* `words_spell.py`：单词拼写
* `words_turn.py`：单词翻转卡片

## 2.辅助脚本
* `get_listen_coordinates.py`
* `get_read_coordinates.py`
* `get_grammar_coordinates.py`
* `get_words_spell_coordinates.py`
* `get_words_turn_coordinates.py`

这些文件多半用于获取或定义页面控件的坐标或区域位置，为主功能脚本提供界面自动化的操作支持

* `__init__.py`：包初始化脚本，使整个目录可以作为一个 Python 包导入使用

## 3.资源文件
资源文件夹 `res/`

* `img/`：存放项目使用到的图片资源（如按钮、logo、图标等）

* `ui/`：存放Ui界面文件和依赖（如 layui 前端UI库）

# 二、开发环境

[AScript](http://dev.airscript.cn/)

脚本基于 AScript 开发，无需电脑即可在手机端直接运行，其官网链接如上。

------

[基于AS的Python自动化脚本开发](https://www.bilibili.com/video/BV1HX4y1i7pf/?share_source=copy_web&vd_source=c4fffa513d6db04895d3e253e3d9cd1a)

此视频可供入手学习，对不会使用的同学友好。

------

由于该小程序有防检测机制，传统的点击和滑动可能失效或者异常，所以作者采用 ESP32-HID 的形式，完成防检测，具体使用视频如下，官网开发文档也有介绍。

[AirScript-windows电脑下Hid模式的介配置与开启](https://www.bilibili.com/video/BV1at9nYXEhg/?share_source=copy_web&vd_source=c4fffa513d6db04895d3e253e3d9cd1a)

因为作者利用 ESP32-S3 开发板，所以选择了 USB-HID 的模式，如需蓝牙 HID，请自行修改源码。

------

<img src="https://cdn.nlark.com/yuque/0/2025/png/42519851/1760678934096-3d49e009-1529-4785-b27c-c667f9d37293.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_0%2Cw_1721%2Ch_535" alt="img" width="400">

由于需要调用 TomatoOcr 插件进行 OCR 识别，但价格昂贵，所以如需许可证，可联系开发者。

# 三、必要设置

因为代码中调取了 TomatoOcr 的文字识别工具，所以需要尽量保证识别区域干净整洁，以防文字识别意外，下附具体设置方法：

<img src="https://cdn.nlark.com/yuque/0/2025/png/42519851/1760202761105-f305f93c-ae57-42d2-b6d9-2bd324071d1f.png" alt="进入小程序" height="200"><img src="https://cdn.nlark.com/yuque/0/2025/png/42519851/1760677743559-60768753-3a1b-4963-a2aa-01cf0e00e178.png" alt="进入我的" height="200"><img src="https://cdn.nlark.com/yuque/0/2025/png/42519851/1760420442737-6d1e2f73-49f9-4d70-ab1b-840946af1ebd.png" alt="皮肤设置内容" height="200"><img src="https://cdn.nlark.com/yuque/0/2025/png/42519851/1760420328453-6571c3c2-e7ba-4fe1-b687-9ef05476a147.png" alt="设置内容" height="200">

# 四、声明

- 本项目完全个人开发，代码开源，但不接受任何对源码封装后的商业行为，请自行遵守社区开源协议！
- 本项目仅用于学习交流！
