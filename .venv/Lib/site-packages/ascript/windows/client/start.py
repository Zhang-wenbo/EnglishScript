import ascript.windows.client.server as server
import ascript.windows.client.ui as ui
import threading


def startServer():
    server.run()

if __name__ == '__main__':
    thread_server = threading.Thread(target=startServer)
    thread_server.start()
    ui.enter()

# home = ui.HomeWindow()
# home.show()


# ui.check_workspace()
