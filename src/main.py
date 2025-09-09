import gradio as gr
import os
from settings import COMFY_WORKFLOWS_PATH, WEBUI_TITLE
from workflow import Element, Workflow
from node_utils import getNodeDataTypeAndValue, DataType, parseMinMaxStep

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")

class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        print(COMFY_WORKFLOWS_PATH, flush=True)
        workflowPath = os.path.join(COMFY_WORKFLOWS_PATH, "wan2_2_flf2v.json")
        with open(workflowPath) as f:
            workflowComfy = f.read()
        self._workflow: Workflow = Workflow(workflowComfy)

    def _getElementUI(self, element: Element):
        node = self._workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        minMaxStep = parseMinMaxStep(element.other_text)

        if dataType == DataType.IMAGE:
            gr.Image(label=element.label)
        elif dataType in (DataType.INT, DataType.FLOAT):
            step = 1 if dataType == DataType.INT else 0.01
            if minMaxStep:
                if minMaxStep[2]:
                    step = minMaxStep[2]
                gr.Slider(value=defaultValue, label=element.label, step=step,
                            minimum=minMaxStep[0], maximum=minMaxStep[1])
            else:
                gr.Number(value=defaultValue, label=element.label, step=step)
        elif dataType == DataType.STRING:
            gr.Textbox(value=defaultValue, label=element.label)
        else:
            gr.Markdown(f"Not yet implemented [{dataType}]: {element.label}")


    def _getCategoryTabUI(self, category: str, tab: str):
        elements = self._workflow.getElements(category, tab)
        for element in elements:
            self._getElementUI(element)


    def _getCategoryUI(self, category: str):
        tabs = self._workflow.getTabs(category)
        if len(tabs) == 0: return
        if len(tabs) == 1:
            self._getCategoryTabUI(category, tabs[0])
        else:
            with gr.Tabs():
                for tab in tabs:
                    with gr.Tab(tab):
                        self._getCategoryTabUI(category, tab)            


    def _getWorkflowUI(self):
        with gr.Blocks(analytics_enabled=False) as workflowUI:
            with gr.Row():
                with gr.Column():
                    self._getCategoryUI("text_prompt")
                    gr.Button("Run")
                    with gr.Accordion("Advanced options", open=False):
                        self._getCategoryUI("advanced_option")
                    self._getCategoryUI(category="image_prompt")
                with gr.Column():
                    gr.Gallery(label="Output placeholder")
                    self._getCategoryUI("important_option")
        return workflowUI
    

    def getWebUI(self):
        with gr.Blocks(analytics_enabled=False, title=WEBUI_TITLE) as webUI:
            self._getWorkflowUI()
        return webUI


if __name__ == "__main__":
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
