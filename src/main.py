import gradio as gr
import os
from settings import COMFY_WORKFLOWS_PATH, WEBUI_TITLE, GRADIO_THEME
from workflow import Workflow
from workflowUI import WorkflowUI

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        workflowNames = os.listdir(COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for name in workflowNames:
            workflowPath = os.path.join(COMFY_WORKFLOWS_PATH, name)
            with open(workflowPath) as f:
                workflowComfy = f.read()
            self._workflows[name.removesuffix(".json")]: Workflow = Workflow(workflowComfy)


    def _onSelectWorkflowCallback(self):
        def callback(name):
            return [gr.Row(visible=x==name) for x in self._workflowUIs.keys()]
        return callback


    def getWebUI(self):
        self._workflowUIs: dict[str, WorkflowUI] = dict()

        with gr.Blocks(analytics_enabled=False,
                       title=WEBUI_TITLE,
                       theme=GRADIO_THEME) as webUI:
            workflowRadioChoices = list(self._workflows.keys())
            workflowsRadio = gr.Radio(choices=workflowRadioChoices,
                            show_label=False, value=workflowRadioChoices[0])
            isFirst = True
            for name in self._workflows.keys():
                self._workflowUIs[name] = WorkflowUI(isFirst, self._workflows[name])
                isFirst = False
            
            with gr.Sidebar(width=100, open=False):
                gr.Button("Button1", variant="huggingface")
                gr.Button("Button2", variant="primary")

            workflowsRadio.select(
                fn=self._onSelectWorkflowCallback(),
                inputs=[workflowsRadio],
                outputs=list([x.ui for x in self._workflowUIs.values()])
            )

        return webUI


if __name__ == "__main__":
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
