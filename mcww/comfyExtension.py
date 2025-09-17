from mcww import opts
import threading
from mcww.mainUI import MinimalisticComfyWrapperWebUI

MCWW: MinimalisticComfyWrapperWebUI = None


def launchInThread():
    global MCWW
    MCWW = MinimalisticComfyWrapperWebUI()
    thread = threading.Thread(target=lambda: MCWW.launch())
    thread.start()


def getPort():
    global MCWW
    if not MCWW or not MCWW.webUI:
        return None
    return MCWW.webUI.server_port
