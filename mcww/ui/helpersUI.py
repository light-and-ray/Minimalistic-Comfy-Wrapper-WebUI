import traceback, subprocess
import gradio as gr
from mcww import opts, shared
from mcww.utils import RESTART_TMP_FILE, saveLogError
from mcww.ui.uiUtils import extractMetadata, ButtonWithConfirm, save_string_to_file
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy import comfyAPI
from mcww.comfy.workflow import Workflow

class HelpersUI:
    def __init__(self):
        self._buildHelpersUI()

    @staticmethod
    def getConsoleLogs():
        try:
            return comfyAPI.getConsoleLogs()
        except Exception as e:
            if type(e) == comfyAPI.ComfyIsNotAvailable:
                return "Comfy is not available"
            saveLogError(e, "Error on get console logs")
            return f"{traceback.format_exc()}"

    @staticmethod
    def restartComfy():
        try:
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

    @staticmethod
    def updateMCWW():
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=opts.MCWW_DIRECTORY,
                check=True,
                text=True,
                capture_output=True
            )
            print(result.stdout)
            gr.Success(result.stdout)
        except subprocess.CalledProcessError as e:
            saveLogError(e, f"Error on git pull, stderr:\n{e.stderr}\nstdout:\n{e.stdout}\n")
            gr.Warning(f"{e.stderr}")
        except Exception as e:
            saveLogError(e, "Error on git pull")
            gr.Warning(f"{e.__class__.__name__}: {e}")

    def restartStandalone(self):
        save_string_to_file("", RESTART_TMP_FILE)
        shared.webUI.close()


    def _buildManagementUI(self):
        with gr.Column():
            with gr.Row():
                comfyConsole = gr.Code(interactive=False, label="Comfy Logs", language="markdown",
                    wrap_lines=True, elem_classes=["comfy-logs-code"], show_line_numbers=False)
                refreshButton = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
                gr.on(
                    triggers=[refreshButton.click, shared.webUI.load],
                    fn=self.getConsoleLogs,
                    outputs=[comfyConsole],
                )
        with gr.Column():
            gr.Markdown("Workflow loading logs will be here")
        with gr.Column():
            updateMCWW = ButtonWithConfirm(label="Update this WebUI (git pull)",
                confirm_label="Confirm update", cancel_label="Cancel update",
            )
            updateMCWW.click(
                fn=self.updateMCWW,
            )
            if opts.IS_STANDALONE:
                restartStandaloneButton = ButtonWithConfirm(label="Restart this WebUI",
                        confirm_label="Confirm restart", cancel_label="Cancel restart"
                )
                restartStandaloneButton.click(
                    fn=self.restartStandalone,
                )
            restartComfyButton = ButtonWithConfirm(
                label="Restart Comfy", confirm_label="Confirm restart", cancel_label="Cancel restart"
            )
            restartComfyButton.click(
                fn=self.restartComfy,
            )


    def _buildMetadataUI(self):
        file = gr.File()
        metadataPrompt = gr.Json(label="Metadata prompt (API)", render=False)
        metadataWorkflow = gr.Json(label="Metadata workflow (Graph)", render=False)

        @gr.render(inputs=[metadataPrompt, metadataWorkflow])
        def renderMetadataWorkflow(metadataPrompt: dict|None, metadataWorkflow: dict|None):
            for metadata in (metadataPrompt, metadataWorkflow):
                try:
                    if not metadata:
                        continue
                    workflow = Workflow(metadata)
                    if not workflow.isValid():
                        continue
                    with gr.Group():
                        WorkflowUI(workflow=workflow, name="", mode=WorkflowUI.Mode.METADATA)
                    return
                except Exception as e:
                    saveLogError(e, "Error on rendering metadata workflow")
                    gr.Markdown(f"{e.__class__.__name__}: {e}", elem_classes=["mcww-visible"])

        metadataPrompt.render()
        metadataWorkflow.render()

        file.change(
            fn=extractMetadata,
            inputs=[file],
            outputs=[metadataPrompt, metadataWorkflow],
        )


    def _buildHelperCompareTab(self):
        with gr.Row(elem_classes=["grid-on-mobile"]):
            imageA = gr.Image(label="A", type="pil", height="250px", elem_classes=["no-compare"])
            swapButton = gr.Button("⇄", elem_classes=["mcww-tool"])
            imageB = gr.Image(label="B", type="pil", height="250px", elem_classes=["no-compare"])
        with gr.Row():
            slider = gr.ImageSlider(show_label=False, height="90vh", elem_classes=["no-compare", "no-copy"],
                    interactive=False, show_download_button=False)

        @gr.on(
            triggers=[imageA.change, imageB.change],
            inputs=[imageA, imageB],
            outputs=[slider],
        )
        def onHelperImageCompareChange(imageA, imageB):
            if not imageA or not imageB:
                return None
            return gr.Slider(value=(imageA, imageB))

        swapButton.click(
            fn=lambda a, b: (b, a),
            inputs=[imageA, imageB],
            outputs=[imageA, imageB],
        )


    @staticmethod
    def _getLoras():
        try:
            loras = comfyAPI.getLoras()
            loras = [f"<lora:{lora.removesuffix('.safetensors')}:1.0>" for lora in loras]
            return loras
        except Exception as e:
            if type(e) == comfyAPI.ComfyIsNotAvailable:
                raise gr.Error("Comfy is not available", print_exception=False)
            saveLogError(e, "Error on get loras")
            raise gr.Error("Unexpected error on get loras. Check logs for details")


    def _buildLorasUI(self):
        title = "Copy loras from here in format for extensions like Prompt Control"
        with gr.Row():
            lorasDataframe = gr.DataFrame(
                value=self._getLoras,
                interactive=False,
                show_label=False,
                headers=[title],
                show_search='filter',
                type="array",
                elem_classes=["mcww-loras-table"],
            )
            refresh = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
            refresh.click(
                fn=self._getLoras,
                outputs=[lorasDataframe],
            )


    def _buildHelpersUI(self):
        with gr.Tabs(visible=False) as self.ui:
            with gr.Tab("Loras"):
                self._buildLorasUI()
            with gr.Tab("Management"):
                self._buildManagementUI()
            with gr.Tab("Metadata"):
                self._buildMetadataUI()
            with gr.Tab("Compare images"):
                self._buildHelperCompareTab()

