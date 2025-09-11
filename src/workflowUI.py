from dataclasses import dataclass
import gradio as gr
from workflow import Element, Workflow
from node_utils import getNodeDataTypeAndValue, DataType, parseMinMaxStep


@dataclass
class ElementUI:
    element: Element
    gradioComponent: gr.Component


class WorkflowUI:
    def __init__(self, isFirst: bool, workflow: Workflow):
        self.ui: gr.Row = None
        self.elements: list[ElementUI] = []
        self.runButton: gr.Button = None
        self._isFirst = isFirst
        self._workflow = workflow
        self._initWorkflowUI()
    
    def _makeElementUI(self, element: Element):
        node = self._workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        minMaxStep = parseMinMaxStep(element.other_text)

        if dataType == DataType.IMAGE:
            component = gr.Image(label=element.label)
        elif dataType in (DataType.INT, DataType.FLOAT):
            step = 1 if dataType == DataType.INT else 0.01
            if minMaxStep:
                if minMaxStep[2]:
                    step = minMaxStep[2]
                component = gr.Slider(value=defaultValue, label=element.label, step=step,
                            minimum=minMaxStep[0], maximum=minMaxStep[1])
            else:
                component = gr.Number(value=defaultValue, label=element.label, step=step)
        elif dataType == DataType.STRING:
            component = gr.Textbox(value=defaultValue, label=element.label)
        else:
            gr.Markdown(f"Not yet implemented [{dataType}]: {element.label}")
            return
        self.elements.append(ElementUI(element=element, gradioComponent=component))


    def _makeCategoryTabUI(self, category: str, tab: str):
        elements = self._workflow.getElements(category, tab)
        for element in elements:
            self._makeElementUI(element)


    def _makeCategoryUI(self, category: str):
        tabs = self._workflow.getTabs(category)
        if len(tabs) == 0: return
        if len(tabs) == 1:
            self._makeCategoryTabUI(category, tabs[0])
        else:
            with gr.Tabs():
                for tab in tabs:
                    with gr.Tab(tab):
                        self._makeCategoryTabUI(category, tab)            


    def _initWorkflowUI(self):
        with gr.Row(visible=self._isFirst) as workflowUI:
            with gr.Column():
                self._makeCategoryUI("text_prompt")
                self.runButton = gr.Button("Run")

                if self._workflow.categoryExists("advanced"):
                    with gr.Accordion("Advanced options", open=False):
                        self._makeCategoryUI("advanced")

                if self._workflow.categoryExists("image_prompt"):
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
            
        self.ui = workflowUI
    

