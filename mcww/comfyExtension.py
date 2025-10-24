from mcww import opts
import threading, os
from mcww.mainUI import MinimalisticComfyWrapperWebUI
from mcww.utils import logoHtml

MCWW: MinimalisticComfyWrapperWebUI = None


def _initOpts():
    import folder_paths
    workflowsDir = os.path.join(folder_paths.user_directory, "default", "workflows")
    subdir = os.getenv("MCWW_WORKFLOW_SUBDIR", "").strip()
    if subdir:
        workflowsDir += subdir
    opts.FILE_CONFIG = opts._FileConfig(mode=opts.FilesMode.SAME_SERVER,
                            input_dir=folder_paths.input_directory,
                            output_dir=folder_paths.output_directory)
    opts.COMFY_WORKFLOWS_PATH = workflowsDir
    from comfy.cli_args import args
    address = "0.0.0.0" if getattr(args, "listen", None) else "127.0.0.1"
    portComfy = str(getattr(args, "port", "8188"))
    if not os.environ.get("GRADIO_SERVER_NAME"):
        os.environ["GRADIO_SERVER_NAME"] = address
    opts.COMFY_ADDRESS = f"localhost:{portComfy}"
    portGradio = os.environ.get("GRADIO_SERVER_PORT", "7860")
    if portComfy == portGradio != "7861":
        os.environ["GRADIO_SERVER_PORT"] = "7861"


def launchInThread():
    _initOpts()
    global MCWW
    MCWW = MinimalisticComfyWrapperWebUI()
    thread = threading.Thread(target=lambda: MCWW.launch())
    thread.daemon = True
    thread.start()


def getPort():
    global MCWW
    if not MCWW or not MCWW.webUI:
        return None
    return MCWW.webUI.server_port


def getLogo():
    return logoHtml
