import gradio as gr
import os
from workflow import Workflow
from workflowUI import WorkflowUI
from utils import ifaceCSS, onIfaceLoadedInjectJS, read_string_from_file
import opts

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        workflowNames = os.listdir(opts.COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for name in workflowNames:
            workflowPath = os.path.join(opts.COMFY_WORKFLOWS_PATH, name)
            workflowComfy = read_string_from_file(workflowPath)
            self._workflows[name.removesuffix(".json")]: Workflow = Workflow(workflowComfy)

    def _onShowQueueClick(self):
        return gr.update(visible=False), gr.update(visible=True)

    def _onHideQueueClick(self):
        return gr.update(visible=True), gr.update(visible=False)


    def getWebUI(self):
        with gr.Blocks(analytics_enabled=False,
                       title=opts.WEBUI_TITLE,
                       theme=opts.GRADIO_THEME,
                       css=ifaceCSS) as webUI:
            with gr.Row():
                choices = list(self._workflows.keys())
                workflowsRadio = gr.Radio(choices=choices, show_label=False, value=choices[0])
            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    for _ in range(5):
                        gr.Gallery(interactive=False)
                with gr.Column():
                    @gr.render(inputs=workflowsRadio)
                    def renderWorkflow(name):
                        WorkflowUI(self._workflows[name])

            with gr.Sidebar(width=100, open=False):
                hideQueueButton = gr.Button("hide queue")
                showQueueButton = gr.Button("show queue")

            showQueueButton.click(
                fn=self._onShowQueueClick,
                inputs=[],
                outputs=[workflowsRadio, queueColumn]
            )
            hideQueueButton.click(
                fn=self._onHideQueueClick,
                inputs=[],
                outputs=[workflowsRadio, queueColumn]
            )
            webUI.load(
                fn=None,
                inputs=[],
                outputs=[],
                js=onIfaceLoadedInjectJS
            )
        return webUI


if __name__ == "__main__":
    opts.initialize()
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
