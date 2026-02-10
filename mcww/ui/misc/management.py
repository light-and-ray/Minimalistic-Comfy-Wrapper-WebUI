import traceback, subprocess, sys, os
import gradio as gr
from urllib.error import HTTPError
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


def restartComfy():
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
            if isinstance(e, HTTPError) and e.code == 404:
                gr.Warning("ComfyUI-Manager is not installed")
            elif isinstance(e, comfyAPI.ComfyIsNotAvailable):
                gr.Warning("Comfy is not available")
            else:
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
            print()
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
            saveLogError(e, f"Error on pip install, stderr:\n{e.stderr}\nstdout:\n{e.stdout}\n")
            raise gr.Error(f"{e.stderr}", print_exception=False)
        except Exception as e:
            saveLogError(e, "Error on pip install")
            raise gr.Error(f"{e.__class__.__name__}: {e}", print_exception=False)
    finally:
        g_is_updating = False


def restartStandalone():
    if g_is_updating:
        gr.Info("Update is not finished yet")
        return
    save_string_to_file("", RESTART_TMP_FILE)
    shared.webUI.close()


def freeCacheAndModels():
    comfyAPI.freeCacheAndMemory()
    gr.Info("Done", duration=3)


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
            wrap_lines=True, elem_classes=["comfy-logs-code", "allow-pwa-select"], show_line_numbers=False)
        refreshButton = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
        gr.Checkbox(interactive=True, label="Auto", value=False,
                elem_classes=["mcww-auto-refresh-checkbox", "mcww-text-button"])
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
                fn=restartStandalone,
            )
        restartComfyButton = ButtonWithConfirm(
            label="Restart Comfy", confirm_label="Confirm restart", cancel_label="Cancel restart",
            elem_classes=["label-button"],
        )
        restartComfyButton.click(
            fn=restartComfy,
        )
        cleanThumbnailsCacheButton = ButtonWithConfirm(
            label="Clean thumbnails cache", confirm_label="Confirm clean", cancel_label="Cancel clean",
            elem_classes=["label-button"],
        )
        cleanThumbnailsCacheButton.click(
            fn=_cleanThumbnails,
        )
        freeCacheAndModelsButton = ButtonWithConfirm(
            label="Free cache and unload models", confirm_label="Confirm free", cancel_label="Cancel free",
            elem_classes=["label-button"],
        )
        freeCacheAndModelsButton.click(
            fn=freeCacheAndModels,
        )

        with gr.Row(equal_height=True, elem_classes=["install-as-pwa-button-row"]):
            installButton = gr.Button("Install as PWA", scale=0, elem_classes=["mcww-text-button"])
            installInfo = gr.Markdown("", elem_classes=["mcww-visible", "info-text"])
        @gr.on(
            triggers=[installButton.click],
            inputs=[shared.dummyComponentBool],
            outputs=[installInfo],
            js="installAsPWA",
        )
        def onInstallButtonClicked(supported):
            if not supported:
                return gr.Markdown(value="*Not supported or already installed. Read "
                    "[this](https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI/blob/master/docs/pwaAndSecureContext.md) "
                    "for details*")
            return gr.Markdown(value="")

