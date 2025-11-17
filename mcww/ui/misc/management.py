import traceback, subprocess, sys, os
import gradio as gr
from mcww import opts, shared, queueing
from mcww.utils import RESTART_TMP_FILE, saveLogError, save_string_to_file
from mcww.ui.uiUtils import ButtonWithConfirm
from mcww.comfy import comfyAPI


def _getConsoleLogs():
    try:
        return comfyAPI.getConsoleLogs()
    except Exception as e:
        if type(e) == comfyAPI.ComfyIsNotAvailable:
            return "Comfy is not available"
        saveLogError(e, "Error on get console logs")
        return f"{traceback.format_exc()}"


g_is_updating = False


def _restartComfy():
    if g_is_updating:
        gr.Info("Update is not finished yet")
        return
    try:
        if not opts.IS_STANDALONE:
            queueing.saveQueue()
        comfyAPI.restartComfy()
    except Exception as e:
        if type(e).__name__ == "RemoteDisconnected":
            gr.Info("Restarting...")
        else:
            if type(e) != comfyAPI.ComfyIsNotAvailable:
                saveLogError(e, "Error on restart Comfy")
            gr.Warning(f"{e.__class__.__name__}: {e}")
    else:
        gr.Warning("Something went wrong")


def _updateMCWW():
    global g_is_updating
    try:
        g_is_updating = True
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=opts.MCWW_DIRECTORY,
                check=True,
                text=True,
                capture_output=True
            )
            print(result.stdout)
            gr.Success(result.stdout, title="Git pull: Success")
        except subprocess.CalledProcessError as e:
            saveLogError(e, f"Error on git pull, stderr:\n{e.stderr}\nstdout:\n{e.stdout}\n")
            raise gr.Error(f"{e.stderr}", print_exception=False)
        except Exception as e:
            saveLogError(e, "Error on git pull")
            raise gr.Error(f"{e.__class__.__name__}: {e}", print_exception=False)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=os.path.join(opts.MCWW_DIRECTORY, ".."),
                check=True,
                text=True,
                capture_output=True
            )
            print(result.stdout)
            gr.Success(result.stdout[:100]+"...", title="pip install: Success")
        except subprocess.CalledProcessError as e:
            saveLogError(e, f"Error on git pull, stderr:\n{e.stderr}\nstdout:\n{e.stdout}\n")
            raise gr.Error(f"{e.stderr}", print_exception=False)
        except Exception as e:
            saveLogError(e, "Error on git pull")
            raise gr.Error(f"{e.__class__.__name__}: {e}", print_exception=False)
    finally:
        g_is_updating = False


def _restartStandalone():
    if g_is_updating:
        gr.Info("Update is not finished yet")
        return
    save_string_to_file("", RESTART_TMP_FILE)
    shared.webUI.close()


def _cleanThumbnails():
    try:
        queueing.queue.cleanThumbnails()
        gr.Success("Cleaned")
    except Exception as e:
        saveLogError(e, "Something went wrong")
        gr.Warning(f"{traceback.format_exc()}")


def buildManagementUI():
    with gr.Row():
        comfyConsole = gr.Code(interactive=False, label="Comfy Logs",
            wrap_lines=True, elem_classes=["comfy-logs-code"], show_line_numbers=False)
        refreshButton = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
        gr.on(
            triggers=[refreshButton.click, shared.webUI.load],
            fn=_getConsoleLogs,
            outputs=[comfyConsole],
        ).then(
            **shared.runJSFunctionKwargs("scrollToComfyLogsBottom")
        )
    with gr.Column(elem_classes=["management-buttons-column"]):
        updateMCWW = ButtonWithConfirm(label="Update this WebUI (git pull && pip install)",
            confirm_label="Confirm update", cancel_label="Cancel update", elem_classes=["label-button"],
        )
        updateMCWW.click(
            fn=_updateMCWW,
        )
        if opts.IS_STANDALONE:
            restartStandaloneButton = ButtonWithConfirm(label="Restart this WebUI",
                    confirm_label="Confirm restart", cancel_label="Cancel restart", elem_classes=["label-button"],
            )
            restartStandaloneButton.click(
                fn=_restartStandalone,
            )
        restartComfyButton = ButtonWithConfirm(
            label="Restart Comfy", confirm_label="Confirm restart", cancel_label="Cancel restart",
            elem_classes=["label-button"],
        )
        restartComfyButton.click(
            fn=_restartComfy,
        )
        cleanThumbnailsCacheButton = ButtonWithConfirm(
            label="Clean thumbnails cache", confirm_label="Confirm clean", cancel_label="Cancel clean",
            elem_classes=["label-button"],
        )
        cleanThumbnailsCacheButton.click(
            fn=_cleanThumbnails,
        )
