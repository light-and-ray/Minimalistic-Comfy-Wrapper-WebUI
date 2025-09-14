from dataclasses import dataclass
import gradio as gr
from workflow import Element, Workflow
from nodeUtils import getNodeDataTypeAndValue, DataType, parseMinMaxStep
from processing import Processing


@dataclass
class ElementUI:
    element: Element
    gradioComponent: gr.Component


class WorkflowUI:
    def __init__(self, workflow: Workflow):
        self.ui: gr.Row = None
        self._inputElements: list[ElementUI] = []
        self._outputElements: list[ElementUI] = []
        self._runButton: gr.Button = None
        self._workflow = workflow
        self._initWorkflowUI()
        self._bindButtons()
    
    def _makeInputElementUI(self, element: Element):
        node = self._workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        minMaxStep = parseMinMaxStep(element.other_text)

        if dataType == DataType.IMAGE:
            component = gr.Image(label=element.label, type="pil", format="png")
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
            component = gr.Textbox(value=defaultValue, label=element.label, lines=2)
        else:
            gr.Markdown(value=f"Not yet implemented [{dataType}]: {element.label}")
            return
        self._inputElements.append(ElementUI(element=element, gradioComponent=component))


    def _makeOutputElementUI(self, element: Element):
        node = self._workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        if dataType == DataType.IMAGE:
            component = gr.Gallery(label=element.label, interactive=False, type="pil", format="png")
        elif dataType in (DataType.INT, DataType.FLOAT, DataType.STRING):
            component = gr.Textbox(value=str(defaultValue), label=element.label, interactive=False)
        else:
            gr.Markdown(value=f"Not yet implemented [{dataType}]: {element.label}")
            return
        self._outputElements.append(ElementUI(element=element, gradioComponent=component))


    def _makeCategoryTabUI(self, category: str, tab: str):
        elements = self._workflow.getElements(category, tab)
        for element in elements:
            if element.category == "output":
                self._makeOutputElementUI(element)
            else:
                self._makeInputElementUI(element)


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
        with gr.Row() as workflowUI:
            with gr.Column():
                self._makeCategoryUI("text_prompt")
                self._runButton = gr.Button("Run")

                if self._workflow.categoryExists("advanced"):
                    with gr.Accordion("Advanced options", open=False):
                        self._makeCategoryUI("advanced")

                if self._workflow.categoryExists("image_prompt"):
                    with gr.Tabs():
                        with gr.Tab("Single"):
                            self._makeCategoryUI("image_prompt")
                        with gr.Tab("Single edit"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch from directory"):
                            gr.Markdown("Work in progress")

            with gr.Column():
                self._makeCategoryUI("output")
                self._makeCategoryUI("important")
            
        self.ui = workflowUI
    

    def _bindButtons(self):
        processing = Processing(workflow=self._workflow, 
                inputElements=[x.element for x in self._inputElements],
                outputElements=[x.element for x in self._outputElements],
            )
        self._runButton.click(
            fn=processing.onRunButtonClick,
            inputs=[x.gradioComponent for x in self._inputElements],
            outputs=[x.gradioComponent for x in self._outputElements],
            postprocess=False,
        )


