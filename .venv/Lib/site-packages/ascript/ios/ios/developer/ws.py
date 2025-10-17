import json

from datetime import datetime
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from ascript.ios.developer.api import utils, oc


def listener():
    class CustomStream:
        def __init__(self, target, name):
            self.target = target
            self.name = name

        def write(self, data):
            #        self.target.write(data)  # 首先写入原始的目标流
            self.process_data(data)  # 然后处理数据

        def flush(self):
            self.target.flush()

        def process_data(self, data):
            # 这里可以添加对stderr或stdout数据的特定处理
            # 例如，你可以将stderr数据写入到一个日志文件中
            # print(f"{self.name}: {data.strip()}", file=sys.__stdout__)  # 仅作为示例，打印到原始stdout
            # str_msg = str(data).rstrip()
            str_msg = str(data)
            # if str_msg.endswith('\n'):
            #     str_msg = str_msg+"+"
            # else:
            #     str_msg = str_msg+"-"
            if len(str_msg) > 0:
                msg = {"msg": str_msg, "type": self.name, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                send_messages(json.dumps(msg))
                utils.recode_loger(str_msg, self.name)
                oc.on_log(msg)

                # 保存原始的stdout和stderr

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # 替换sys.stdout和sys.stderr
    sys.stdout = CustomStream(original_stdout, 'i')
    sys.stderr = CustomStream(original_stderr, 'e')


# clients = []

class SimpleEcho(WebSocket):
    def handleMessage(self):
        # 回声（echo）消息
        pass

    def handleConnected(self):
        pass

    #        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


server = None


def start_server():
    global server
    # print("ws://0.0.0.0:9098")
    server = SimpleWebSocketServer('0.0.0.0', 10102, SimpleEcho)
    server.serveforever()


# 在子线程中启动WebSocket服务器
import threading


def send_messages(msg):
    global server
    if server:
        #        print("共连接:",len(server.connections.values()))
        try:
            for client in server.connections.values():
                client.sendMessage(msg)
        except Exception as e:
            print(e)


def run_server_in_thread():
    start_server()


def run():
    # 在子线程中启动WebSocket服务器
    thread = threading.Thread(target=run_server_in_thread, daemon=True)
    thread.start()
    utils.threads.append(thread.ident)

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()
    utils.threads.append(thread.ident)
