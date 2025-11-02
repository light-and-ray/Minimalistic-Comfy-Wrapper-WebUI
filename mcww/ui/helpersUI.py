import traceback
import gradio as gr
from mcww.ui.uiUtils import extractMetadata
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy import comfyAPI
from mcww.comfy.workflow import Workflow

class HelpersUI:
    def __init__(self, mainUIPageRadio: gr.Radio, webUI: gr.Blocks):
        self.mainUIPageRadio = mainUIPageRadio
        self.webUI = webUI
        self._buildHelpersUI()

    def getConsoleLogs(self):
        try:
            return comfyAPI.getConsoleLogs()
        except Exception as e:
            if type(e) == comfyAPI.ComfyIsNotAvailable:
                return "Comfy is not available"
            return f"{traceback.format_exc()}"

    def _buildDebugUI(self):
        with gr.Row():
            with gr.Column():
                comfyConsole = gr.Code(interactive=False, label="Comfy Logs", language="markdown",
                    wrap_lines=True, elem_classes=["comfy-logs-code"], show_line_numbers=False)
                refreshButton = gr.Button("Refresh", scale=0)
                gr.on(
                    triggers=[refreshButton.click, self.webUI.load],
                    fn=self.getConsoleLogs,
                    outputs=[comfyConsole],
                )
        with gr.Row():
            gr.Markdown("Workflow loading logs will be here")


    def _buildMetadataUI(self):
        file = gr.File()
        metadata = gr.Json(label="Metadata", render=False)

        @gr.render(inputs=[metadata])
        def _(metadata: dict|None):
            if not metadata: return
            try:
                workflow = Workflow(metadata)
                if not workflow.isValid():
                    return
                with gr.Group():
                    WorkflowUI(workflow=workflow, name="", mode=WorkflowUI.Mode.METADATA)
            except Exception as e:
                gr.Markdown(f"{e.__class__.__name__}: {e}", elem_classes=["mcww-visible"])

        metadata.render()

        file.change(
            fn=extractMetadata,
            inputs=[file],
            outputs=[metadata],
        )


    def _buildHelpersUI(self):
        with gr.Tabs(visible=False) as helpersUI:
            with gr.Tab("Loras"):
                gr.Markdown("Loras helper will be here")
            with gr.Tab("Debug"):
                self._buildDebugUI()
            with gr.Tab("Metadata"):
                self._buildMetadataUI()

        @gr.on(
            triggers=[self.mainUIPageRadio.change],
            inputs=[self.mainUIPageRadio],
            outputs=[helpersUI]
        )
        def _(mainUIPage: str):
            if mainUIPage == "helpers":
                return gr.Tabs(visible=True)
            else:
                return gr.Tabs(visible=False)

