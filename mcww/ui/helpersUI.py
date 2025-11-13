import traceback, subprocess
import gradio as gr
from mcww import opts, shared, queueing
from mcww.utils import RESTART_TMP_FILE, saveLogError
from mcww.ui.uiUtils import extractMetadata, ButtonWithConfirm, save_string_to_file
from mcww.ui.workflowUI import WorkflowUI
from mcww.ui.compareUI import buildHelperCompareTab
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


    @staticmethod
    def _getLorasState():
        try:
            loras = comfyAPI.getLoras()
            loras = [lora.removesuffix('.safetensors') for lora in loras]
            return loras
        except Exception as e:
            if type(e) == comfyAPI.ComfyIsNotAvailable:
                gr.Warning("Comfy is not available")
            else:
                saveLogError(e, "Error on get loras state")
                gr.Warning("Unexpected error on get loras state. Check logs for details")
        return None


    @staticmethod
    def _getLorasTable(loras: list[str], filter: str = ""):
        try:
            if not loras: return None
            filter = filter.lower()
            table = ""
            table += "|    |\n"
            table += "|----|\n"
            for lora in loras:
                if filter and filter not in lora.lower():
                    continue
                table += f"| `<lora:{lora}:1.0>` |\n"
            return table
        except Exception as e:
            saveLogError(e, "Error on get loras table")
            gr.Warning("Unexpected error on get loras table. Check logs for details")
        return None


    def _buildLorasUI(self):
        self._getLorasTable
        with gr.Column():
            lorasState = gr.State()
            with gr.Row(equal_height=True, elem_classes=["vertically-centred"]):
                gr.Markdown("### Copy loras from here in format for extensions like Prompt Control")
                filter = gr.Textbox(label="Filter", value="", elem_classes=["mcww-loras-filter"])
            with gr.Row():
                lorasTableComponent = gr.Markdown(elem_classes=["mcww-loras-table"])
                refresh = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
            gr.on(
                triggers=[filter.change, lorasState.change],
                fn=self._getLorasTable,
                inputs=[lorasState, filter],
                outputs=[lorasTableComponent],
            )
            gr.on(
                triggers=[refresh.click, shared.webUI.load],
                fn=self._getLorasState,
                outputs=[lorasState],
            )


    def _buildHelpersUI(self):
        with gr.Tabs(visible=False, elem_classes=["tabs-with-hotkeys"]) as self.ui:
            with gr.Tab("Loras"):
                self._buildLorasUI()
            with gr.Tab("Management"):
                self._buildManagementUI()
            with gr.Tab("Metadata"):
                self._buildMetadataUI()
            with gr.Tab("Compare images"):
                buildHelperCompareTab()

