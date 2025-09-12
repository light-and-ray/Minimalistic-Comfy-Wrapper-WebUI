import gradio as gr
import os
from settings import COMFY_WORKFLOWS_PATH, WEBUI_TITLE, GRADIO_THEME
from workflow import Workflow
from workflowUI import WorkflowUI

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        self._queueVisible = False
        workflowNames = os.listdir(COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for name in workflowNames:
            workflowPath = os.path.join(COMFY_WORKFLOWS_PATH, name)
            with open(workflowPath) as f:
                workflowComfy = f.read()
            self._workflows[name.removesuffix(".json")]: Workflow = Workflow(workflowComfy)


    def _onSelectWorkflow(self, name):
        return [gr.Row(visible=x==name) for x in self._workflowUIs.keys()]

    def _onToggleQueueClick(self):
        if self._queueVisible:
            self._queueVisible = False
            return gr.update(visible=True), gr.update(visible=False)
        else:
            self._queueVisible = True
            return gr.update(visible=False), gr.update(visible=True)


    def getWebUI(self):
        self._workflowUIs: dict[str, WorkflowUI] = dict()

        with gr.Blocks(analytics_enabled=False,
                       title=WEBUI_TITLE,
                       theme=GRADIO_THEME) as webUI:
            with gr.Row():
                choices = list(self._workflows.keys())
                workflowsRadio = gr.Radio(choices=choices, show_label=False, value=choices[0])
            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    gr.Gallery(interactive=False)
                    gr.Gallery(interactive=False)
                    gr.Gallery(interactive=False)
                    gr.Gallery(interactive=False)
                    gr.Gallery(interactive=False)
                with gr.Column():
                    isFirst = True
                    for name in self._workflows.keys():
                        self._workflowUIs[name] = WorkflowUI(isFirst, self._workflows[name])
                        isFirst = False
            
            with gr.Sidebar(width=100, open=False):
                toggleQueueButton = gr.Button("toggle queue")

            workflowsRadio.select(
                fn=self._onSelectWorkflow,
                inputs=[workflowsRadio],
                outputs=list([x.ui for x in self._workflowUIs.values()])
            )

            toggleQueueButton.click(
                fn=self._onToggleQueueClick,
                inputs=[],
                outputs=[workflowsRadio, queueColumn]
            )

        return webUI


if __name__ == "__main__":
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
