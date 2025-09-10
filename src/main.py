import gradio as gr
import os
from settings import COMFY_WORKFLOWS_PATH, WEBUI_TITLE, GRADIO_THEME
from workflow import Element, Workflow
from node_utils import getNodeDataTypeAndValue, DataType, parseMinMaxStep


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

    def _makeElementUI(self, element: Element):
        node = self._currentWorkflow().getOriginalWorkflow()[element.index]
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


    def _makeCategoryTabUI(self, category: str, tab: str):
        elements = self._currentWorkflow().getElements(category, tab)
        for element in elements:
            self._makeElementUI(element)


    def _makeCategoryUI(self, category: str):
        tabs = self._currentWorkflow().getTabs(category)
        if len(tabs) == 0: return
        if len(tabs) == 1:
            self._makeCategoryTabUI(category, tabs[0])
        else:
            with gr.Tabs():
                for tab in tabs:
                    with gr.Tab(tab):
                        self._makeCategoryTabUI(category, tab)            


    def _makeWorkflowUI(self):
        isFirstWorkflow = len(self._workflowToUI) == 0
        with gr.Row(visible=isFirstWorkflow) as workflowUI:
            with gr.Column():
                self._makeCategoryUI("text_prompt")
                gr.Button("Run")

                if self._currentWorkflow().categoryExists("advanced"):
                    with gr.Accordion("Advanced options", open=False):
                        self._makeCategoryUI("advanced")

                if self._currentWorkflow().categoryExists("image_prompt"):
                    with gr.Tabs():
                        with gr.Tab("Single"):
                            self._makeCategoryUI(category="image_prompt")
                        with gr.Tab("Single edit"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch from directory"):
                            gr.Markdown("Work in progress")

            with gr.Column():
                gr.Gallery(label="Output placeholder", interactive=False)
                self._makeCategoryUI("important")
            
        self._workflowToUI[self._currentWorkflowName] = workflowUI
    

    def _currentWorkflow(self):
        return self._workflows[self._currentWorkflowName]


    def _onSelectWorkflowCallback(self):
        def callback(name):
            return [gr.Row(visible=x==name) for x in self._workflowToUI.keys()]
        return callback


    def getWebUI(self):
        self._components: dict[str, list[gr.Component]] = []
        self._workflowToUI: dict[str, gr.Row] = dict()

        with gr.Blocks(analytics_enabled=False,
                       title=WEBUI_TITLE,
                       theme=GRADIO_THEME) as webUI:
            workflowRadioChoices = list(self._workflows.keys())
            workflowsRadio = gr.Radio(choices=workflowRadioChoices,
                            show_label=False, value=workflowRadioChoices[0])
            for self._currentWorkflowName in self._workflows.keys():
                self._makeWorkflowUI()
            
            with gr.Sidebar(width=100, open=False):
                gr.Button("Button1", variant="huggingface")
                gr.Button("Button2", variant="primary")

            workflowsRadio.select(
                fn=self._onSelectWorkflowCallback(),
                inputs=[workflowsRadio],
                outputs=list(self._workflowToUI.values())
            )

        return webUI


if __name__ == "__main__":
    MinimalisticComfyWrapperWebUI().getWebUI().launch()
