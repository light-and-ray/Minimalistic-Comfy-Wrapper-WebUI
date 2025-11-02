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
                    gr.Markdown(f"{e.__class__.__name__}: {e}", elem_classes=["mcww-visible"])

        metadataPrompt.render()
        metadataWorkflow.render()

        file.change(
            fn=extractMetadata,
            inputs=[file],
            outputs=[metadataPrompt, metadataWorkflow],
        )


    def _buildHelperCompareTab(self):
        with gr.Row():
            imageA = gr.Image(label="A", type="pil", height="250px", elem_classes=["no-compare"])
            swapButton = gr.Button("⇄", elem_classes=["mcww-tool"])
            imageB = gr.Image(label="B", type="pil", height="250px", elem_classes=["no-compare"])
        with gr.Row():
            slider = gr.ImageSlider(show_label=False, height="90vh", elem_classes=["no-compare"],
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


    def _buildHelpersUI(self):
        with gr.Tabs(visible=False) as self.ui:
            with gr.Tab("Loras"):
                gr.Markdown("Loras helper will be here")
            with gr.Tab("Debug"):
                self._buildDebugUI()
            with gr.Tab("Metadata"):
                self._buildMetadataUI()
            with gr.Tab("Compare images"):
                self._buildHelperCompareTab()

