from dataclasses import dataclass
import gradio as gr
from mcww.workflow import Element, Workflow
from mcww.nodeUtils import getNodeDataTypeAndValue, parseMinMaxStep
from mcww.utils import DataType
from mcww import queueing

@dataclass
class ElementUI:
    element: Element
    gradioComponent: gr.Component


class WorkflowUI:
    def __init__(self, workflow: Workflow, name, queueMode: bool, pullOutputsKey: str|None = None):
        self.ui: gr.Row = None
        self.name = name
        self.pullOutputsKey = pullOutputsKey
        self.inputElements: list[ElementUI] = []
        self.outputElements: list[ElementUI] = []
        self.runButton: gr.Button = None
        self.workflow = workflow
        self._queueMode = queueMode
        self._buildWorkflowUI()

    def _makeInputElementUI(self, element: Element):
        node = self.workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        minMaxStep = parseMinMaxStep(element.other_text)

        if dataType == DataType.IMAGE:
            component = gr.Image(label=element.label, type="pil", height="min(80vh, 500px)", render=False)
        elif dataType in (DataType.INT, DataType.FLOAT):
            step = 1 if dataType == DataType.INT else 0.01
            if minMaxStep:
                if minMaxStep[2]:
                    step = minMaxStep[2]
                component = gr.Slider(value=defaultValue, label=element.label, step=step,
                            minimum=minMaxStep[0], maximum=minMaxStep[1], show_reset_button=False, render=False)
            else:
                component = gr.Number(value=defaultValue, label=element.label, step=step, render=False)
        elif dataType == DataType.STRING:
            component = gr.Textbox(value=defaultValue, label=element.label, lines=2, render=False)
        elif dataType == DataType.VIDEO:
            component = gr.Video(label=element.label, height="min(80vh, 500px)", render=False)
        else:
            gr.Markdown(value=f"Not yet implemented [{dataType}]: {element.label}")
            return
        if element.isSeed() and dataType == DataType.INT and not self._queueMode:
            with gr.Row(equal_height=True):
                component.render()
                component.value = -1
                randomButton = gr.Button(value="🎲", elem_classes=["mcww-tool"])
                randomButton.click(fn=lambda: -1, outputs=[component])
                reuseButton = gr.Button(value="♻️", elem_classes=["mcww-tool"])
                reuseButton.click(
                    fn=queueing.queue.getOnPullPreviousUsedSeed(self.pullOutputsKey, element.getKey()),
                    outputs=[component])
        else:
            component.render()
        if self._queueMode:
            component.interactive = False
        self.inputElements.append(ElementUI(element=element, gradioComponent=component))


    def _makeOutputElementUI(self, element: Element):
        node = self.workflow.getOriginalWorkflow()[element.index]
        dataType, defaultValue = getNodeDataTypeAndValue(node)
        if dataType in (DataType.IMAGE, DataType.VIDEO):
            component = gr.Gallery(label=element.label, interactive=False, type="pil", format="png")
        elif dataType in (DataType.INT, DataType.FLOAT, DataType.STRING):
            component = gr.Textbox(value=str(defaultValue), label=element.label, interactive=False)
        else:
            gr.Markdown(value=f"Not yet implemented [{dataType}]: {element.label}")
            return
        self.outputElements.append(ElementUI(element=element, gradioComponent=component))


    def _makeCategoryTabUI(self, category: str, tab: str):
        elements = self.workflow.getElements(category, tab)
        for element in elements:
            if element.category == "output":
                self._makeOutputElementUI(element)
            else:
                self._makeInputElementUI(element)


    def _makeCategoryUI(self, category: str):
        tabs = self.workflow.getTabs(category)
        if len(tabs) == 0: return
        if len(tabs) == 1:
            self._makeCategoryTabUI(category, tabs[0])
        else:
            with gr.Tabs():
                for tab in tabs:
                    with gr.Tab(tab):
                        self._makeCategoryTabUI(category, tab)


    def _buildWorkflowUI(self):
        uiClasses = ["active-workflow-ui"]
        if not self._queueMode:
            uiClasses.append("resize-handle-row")
        with gr.Row(elem_classes=uiClasses) as workflowUI:
            with gr.Column(scale=15):
                self._makeCategoryUI("text_prompt")
                if not self._queueMode:
                    self.runButton = gr.Button("Run")

                if self.workflow.categoryExists("advanced"):
                    with gr.Accordion("Advanced options", open=False):
                        self._makeCategoryUI("advanced")

                if (self.workflow.categoryExists("image_prompt") or
                    self.workflow.categoryExists("video_prompt")
                ):
                    with gr.Tabs():
                        with gr.Tab("Single"):
                            self._makeCategoryUI("image_prompt")
                            self._makeCategoryUI("video_prompt")
                        with gr.Tab("Single edit"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch"):
                            gr.Markdown("Work in progress")
                        with gr.Tab("Batch from directory"):
                            gr.Markdown("Work in progress")
            with gr.Column(scale=15):
                self._makeCategoryUI("output")
                self._makeCategoryUI("important")

        self.ui = workflowUI


