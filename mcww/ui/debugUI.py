import traceback
import gradio as gr
from mcww.comfy import comfyAPI
from mcww.comfy.comfyUtils import ComfyIsNotAvailable

class DebugUI:
    def __init__(self, webUI: gr.Blocks):
        self.webUI = webUI
        self._buildDebugUI()

    def getConsoleLogs(self):
        try:
            return comfyAPI.getConsoleLogs()
        except Exception as e:
            if type(e) == ComfyIsNotAvailable:
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