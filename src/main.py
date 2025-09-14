import uuid
import gradio as gr
import os
from workflow import Workflow
from workflowUI import WorkflowUI
from utils import ifaceCSS, onIfaceLoadedInjectJS, read_string_from_file
import opts

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        self._workflows: dict[str, Workflow] = dict()


    def _onShowQueueClick(self):
        return gr.update(visible=False), gr.update(visible=True)


    def _onHideQueueClick(self):
        return gr.update(visible=True), gr.update(visible=False)


    def _onRefreshWorkflows(self, selected):
        files = os.listdir(opts.COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for file in files:
            if not file.endswith(".json"): continue
            workflowPath = os.path.join(opts.COMFY_WORKFLOWS_PATH, file)
            workflowComfy = read_string_from_file(workflowPath)
            self._workflows[file.removesuffix(".json")]: Workflow = Workflow(workflowComfy)
        choices = list(self._workflows.keys())
        if selected in choices:
            value = selected
        else:
            value= choices[0]
        return gr.Radio(choices=choices, value=value), str(uuid.uuid4())


    def getWebUI(self):
        with gr.Blocks(analytics_enabled=False,
                       title=opts.WEBUI_TITLE,
                       theme=opts.GRADIO_THEME,
                       css=ifaceCSS) as webUI:
            with gr.Row():
                with gr.Column(scale=20):
                    workflowsRadio = gr.Radio(show_label=False)
                with gr.Column(scale=1):
                    refreshWorkflowsButton = gr.Button("Refresh")
                    refreshWorkflowTrigger = gr.Textbox(visible=False)
            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    for _ in range(5):
                        gr.Gallery(interactive=False)
                with gr.Column():
                    @gr.render(
                        inputs=workflowsRadio,
                        triggers=[refreshWorkflowTrigger.change, workflowsRadio.change],
                    )
                    def renderWorkflow(name):
                        WorkflowUI(self._workflows[name])

            with gr.Sidebar(width=100, open=False):
                hideQueueButton = gr.Button("hide queue")
                showQueueButton = gr.Button("show queue")

            refreshWorkflowsKwargs = dict(
                fn=self._onRefreshWorkflows,
                inputs=[workflowsRadio],
                outputs=[workflowsRadio, refreshWorkflowTrigger]
            )

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
            webUI.load(
                **refreshWorkflowsKwargs
            )
            refreshWorkflowsButton.click(
                **refreshWorkflowsKwargs
            )
        return webUI


if __name__ == "__main__":
    opts.initialize()
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
