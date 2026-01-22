from mcww import opts
import threading, os
from mcww.ui.mainUI import MinimalisticComfyWrapperWebUI
from mcww.ui.uiUtils import logoHtml

MCWW: MinimalisticComfyWrapperWebUI = None


def _initOpts():
    import folder_paths
    opts.FILE_CONFIG = opts._FileConfig(mode=opts.FilesMode.SAME_SERVER,
                            input_dir=folder_paths.input_directory,
                            output_dir=folder_paths.output_directory)
    from comfy.cli_args import args
    portComfy = str(getattr(args, "port", "8188"))
    if not os.environ.get("GRADIO_SERVER_NAME"):
        os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0" if "0.0.0.0" in getattr(args, "listen", "") else "127.0.0.1"
    opts.COMFY_ADDRESS = f"localhost:{portComfy}"
    portGradio = os.environ.get("GRADIO_SERVER_PORT", "7860")
    if portComfy == portGradio != "7861":
        os.environ["GRADIO_SERVER_PORT"] = "7861"
    opts.IS_STANDALONE = False
    os.makedirs(opts.STORAGE_DIRECTORY, exist_ok=True)
    opts.initializeOptions()


def launchInThread():
    _initOpts()
    global MCWW
    MCWW = MinimalisticComfyWrapperWebUI()
    thread = threading.Thread(target=lambda: MCWW.launch())
    thread.daemon = True
    thread.start()


def availableAt():
    global MCWW
    if not MCWW or not MCWW.webUI:
        return None
    port = MCWW.webUI.server_port
    shareUrl = MCWW.webUI.share_url
    shareUrlOverride = os.environ.get("COMFY_MCWW_BUTTON_URL_OVERRIDE")
    if shareUrlOverride:
        shareUrl = shareUrlOverride
    return {"port": port, "shareUrl": shareUrl}


def getLogo():
    return logoHtml
