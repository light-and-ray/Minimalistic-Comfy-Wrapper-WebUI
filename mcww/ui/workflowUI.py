from dataclasses import dataclass
from enum import Enum
import gradio as gr
import uuid
from mcww import queueing, shared, opts
from mcww.comfy.comfyFile import ComfyFile
from mcww.utils import DataType
from mcww.ui.presetsUI import renderPresetsInWorkflowUI
from mcww.ui.uiUtils import renderHolidaySpecial, JsonTextbox
from mcww.comfy.workflow import Element, Workflow


@dataclass
class ElementUI:
    element: Element
    gradioComponent: gr.Component
    extraKey: str = ""


class WorkflowUI:
    class Mode(Enum):
        PROJECT = "project"
        QUEUE = "queue"
        METADATA = "metadata"

    def __init__(self, workflow: Workflow, name, mode: Mode, pullOutputsKey: str|None = None):
        self.name = name
        self.pullOutputsKey = pullOutputsKey
        self.inputElements: list[ElementUI] = []
        self.outputElements: list[ElementUI] = []
        self.selectedMediaTabComponent: gr.Textbox = None
        self.mediaSingleElements: list[ElementUI] = []
        self.mediaBatchElements: list[ElementUI] = []
        self.workflow = workflow
        self.outputRunningHtml: gr.HTML = None
        self.outputErrorMarkdown: gr.Markdown = None
        self._textPromptElementUiList: list[ElementUI] = []
        self._mode = mode
        self._buildWorkflowUI()


    def _makeInputElementUI(self, element: Element, allowedTypes: list[DataType]|None = None, forMediaSingle=False):
        if allowedTypes and element.field.type not in allowedTypes:
            return
        minMaxStep = element.parseMinMaxStep()
        showDefault = element.showDefault() or self._mode == self.Mode.METADATA

        if element.field.type == DataType.IMAGE:
            component = gr.Image(label=element.label, type="pil", height="min(80vh, 500px)", render=False)
        elif element.field.type in (DataType.INT, DataType.FLOAT):
            step = 1 if element.field.type == DataType.INT else 0.01
            if minMaxStep:
                if minMaxStep[2]:
                    step = minMaxStep[2]
                component = gr.Slider(value=element.field.defaultValue, label=element.label, step=step,
                            minimum=minMaxStep[0], maximum=minMaxStep[1], show_reset_button=False, render=False)
            else:
                component = gr.Number(value=element.field.defaultValue, label=element.label, step=step, render=False)
        elif element.field.type == DataType.STRING:
            if element.isJson():
                textboxClass = JsonTextbox
            else:
                textboxClass = gr.Textbox
            component = textboxClass(value=element.field.defaultValue, label=element.label, lines=2, render=False)
        elif element.field.type == DataType.VIDEO:
            component = gr.Video(label=element.label, height="min(80vh, 500px)", loop=True, render=False, elem_classes=["mcww-other-gallery"])
        elif element.field.type == DataType.AUDIO:
            component = gr.Audio(label=element.label, render=False, show_download_button=True, elem_classes=["mcww-other-gallery"])
        else:
            gr.Markdown(value=f"Not yet implemented [{element.field.type}]: {element.label}")
            return

        if element.isSeed() and element.field.type == DataType.INT and self._mode == self.Mode.PROJECT:
            with gr.Row(elem_classes=["vertically-centred"]):
                component.render()
                component.value = -1
                randomButton = gr.Button(value="🎲", elem_classes=["mcww-tool"])
                randomButton.click(fn=lambda: -1, outputs=[component])
                reuseButton = gr.Button(value="♻️", elem_classes=["mcww-tool"])
                reuseButton.click(
                    fn=queueing.queue.getOnPullPreviousUsedSeed(self.pullOutputsKey, element.getKey()),
                    outputs=[component])
        elif element.field.type == DataType.IMAGE and self._mode == self.Mode.PROJECT:
            with gr.Column(elem_classes=["input-image-column", f"mcww-key-{str(uuid.uuid4())}"]):
                component.render()
                with gr.Row(elem_classes=["block-row-column", "right-aligned"]):
                    returnButton = gr.Button("Return 🡒", visible=False, elem_classes=["mcww-text-button", "small-button", "return-button"])
                    gr.Button("Open in editor", elem_classes=["open-in-image-editor-button", "mcww-text-button"], scale=0)
                    showReturnButton = gr.Button(elem_classes=["mcww-hidden", "show-return-button"])
                    showReturnButton.click(
                        fn=lambda: gr.Button(visible=True),
                        outputs=[returnButton],
                    )
                    returnButton.click(
                        **shared.runJSFunctionKwargs("openImageEditor")
                    )

        else:
            component.render()
        if self._mode in [self.Mode.QUEUE, self.Mode.METADATA]:
            component.interactive = False
        elementUI = ElementUI(element=element, gradioComponent=component)
        if not forMediaSingle:
            self.inputElements.append(elementUI)
        else:
            self.mediaSingleElements.append(elementUI)
        if element.field.type in (DataType.IMAGE, DataType.VIDEO, DataType.AUDIO):
            if showDefault and isinstance(element.field.defaultValue, ComfyFile):
                component.value = element.field.defaultValue.getGradioInputForComponentInit()
        return elementUI


    def _makeMediaBatchElementUI(self, element: Element, allowedTypes: list[DataType]|None = None):
        if allowedTypes and element.field.type not in allowedTypes:
            return
        elem_classes = []
        if self._mode == self.Mode.PROJECT:
            elem_classes.append("upload-gallery")
        component = gr.Gallery(label=element.label, height="min(80vh, 500px)", elem_classes=elem_classes)
        if self._mode in [self.Mode.QUEUE, self.Mode.METADATA]:
            component.interactive = False
        elementUI = ElementUI(element=element, gradioComponent=component, extraKey="mediaBatch")
        self.mediaBatchElements.append(elementUI)
        return elementUI


    def _makeOutputElementUI(self, element: Element):
        if element.field.type in (DataType.IMAGE, DataType.VIDEO):
            elem_classes = []
            if element.field.type == DataType.VIDEO:
                elem_classes += ["no-compare", "no-copy"]
            component = gr.Gallery(label=element.label, interactive=False, elem_classes=elem_classes)
        elif element.field.type == DataType.AUDIO:
            component = gr.Audio(label=element.label, interactive=False, show_download_button=True, elem_classes=["mcww-other-gallery"])
        else:
            gr.Markdown(value=f"Not yet implemented [{element.field.type}]: {element.label}")
            return
        self.outputElements.append(ElementUI(element=element, gradioComponent=component))


    def _getAllowedForPromptType(self, promptType: str):
        if promptType.startswith("media"):
            allowed: list = [DataType.IMAGE, DataType.VIDEO]
        elif promptType == "text":
            allowed: list = [DataType.STRING]
        elif promptType == "other":
            allowed: list = [DataType.FLOAT, DataType.INT, DataType.AUDIO]
        else:
            raise Exception("Can't be here")
        return allowed


    def _makeCategoryTabUI(self, category: str, tab: str, promptType: str|None):
        elements = self.workflow.getElementsRows(category, tab)
        for elementsRow in elements:
            with gr.Row() if elementsRow else None:
                for element in elementsRow:
                    if category == "output":
                        self._makeOutputElementUI(element)
                    elif category == "prompt":
                        allowed = self._getAllowedForPromptType(promptType)
                        if promptType in ["mediaSingle", "text", "other"]:
                            forMediaSingle = promptType == "mediaSingle"
                            newElementUI = self._makeInputElementUI(element, allowedTypes=allowed, forMediaSingle=forMediaSingle)
                            if promptType == "text" and newElementUI:
                                self._textPromptElementUiList.append(newElementUI)
                        elif promptType == "mediaBatch":
                            self._makeMediaBatchElementUI(element, allowedTypes=allowed)
                    else:
                        self._makeInputElementUI(element)
        if self._mode == self.Mode.PROJECT and category == "prompt" and promptType == "text":
            renderPresetsInWorkflowUI(self.name, self._textPromptElementUiList)


    def _getTabs(self, category: str, promptType: str|None):
        tabs = self.workflow.getTabs(category)
        if not promptType:
            return tabs
        allowed = self._getAllowedForPromptType(promptType)
        filteredTabs = []
        for tab in tabs:
            elements = self.workflow.getElementsRows(category, tab)
            filteredElements = []
            for elementsRow in elements:
                for element in elementsRow:
                    if element.field.type in allowed:
                        filteredElements.append(element)
            if filteredElements:
                filteredTabs.append(tab)
        return filteredTabs


    def _makeCategoryUI(self, category: str, promptType: str|None = None):
        tabs: list[str] = self._getTabs(category, promptType)
        if len(tabs) == 0: return
        elif len(tabs) == 1:
            self._makeCategoryTabUI(category, tabs[0], promptType)
        else:
            tabsClasses = []
            if category == "prompt" and promptType.startswith("media"):
                tabsClasses.append("project-media-prompt-tabs")
                tabsClasses.append(promptType)
            with gr.Tabs(elem_classes=tabsClasses):
                for tab in tabs:
                    with gr.Tab(tab):
                        self._makeCategoryTabUI(category, tab, promptType)


    def _buildWorkflowUI(self):
        uiClasses = ["active-workflow-ui"]
        if self._mode in [self.Mode.PROJECT]:
            uiClasses.append("resize-handle-row")
            uiClasses.append(f"mcww-key-workflow-{self.pullOutputsKey}")
        advancedOptionsOpen = self._mode in [self.Mode.METADATA] or opts.options.openAccordionsAutomatically
        renderHolidaySpecial()
        with gr.Row(elem_classes=uiClasses):
            with gr.Column(scale=15):
                self._makeCategoryUI("prompt", "text")

                if self._mode == self.Mode.PROJECT and opts.options.showRunButtonCopy:
                    runButtonCopy = gr.Button("Run")
                    runButtonCopy.click(
                        **shared.runJSFunctionKwargs("onRunButtonCopyClick")
                    )

                if self.workflow.categoryExists("advanced"):
                    with gr.Accordion("Advanced options", open=advancedOptionsOpen):
                        self._makeCategoryUI("advanced")

                self.selectedMediaTabComponent = gr.Textbox(visible=False, value="tabSingle")
                if self._mode == self.Mode.PROJECT:
                    with gr.Tabs() as mediaCategoryUI:
                        with gr.Tab("Single") as tabSingle:
                            self._makeCategoryUI("prompt", "mediaSingle")
                        with gr.Tab("Batch") as tabBatch:
                            self._makeCategoryUI("prompt", "mediaBatch")
                            if len(self.mediaBatchElements) > 1:
                                gr.Markdown("When there are more then 1 inputs for batch mode, the biggest list "
                                    "of files will be used and the smaller will repeat",
                                        elem_classes=["mcww-visible", "info-text"])
                        with gr.Tab("Batch from directory") as tabBatchFromDir:
                            gr.Markdown("Work in progress", elem_classes=["mcww-visible"])
                        tabSingle.select(fn=lambda: "tabSingle", outputs=[self.selectedMediaTabComponent])
                        tabBatch.select(fn=lambda: "tabBatch", outputs=[self.selectedMediaTabComponent])
                        tabBatchFromDir.select(fn=lambda: "tabBatchFromDir", outputs=[self.selectedMediaTabComponent])
                    if len(self.mediaSingleElements) == 0:
                        mediaCategoryUI.visible = False
                elif self._mode == self.Mode.METADATA:
                    self._makeCategoryUI("prompt", "mediaSingle")
                elif self._mode == self.Mode.QUEUE:
                    self._makeCategoryUI("prompt", "mediaBatch")
                self._makeCategoryUI("prompt", "other")
                for customCategory in self.workflow.getCustomCategories():
                    with gr.Accordion(label=customCategory, open=opts.options.openAccordionsAutomatically):
                        self._makeCategoryUI(customCategory)
                if self._mode == self.Mode.METADATA:
                    self._makeCategoryUI("important")
            if self._mode in [self.Mode.QUEUE, self.Mode.PROJECT]:
                with gr.Column(scale=15):
                    self._makeCategoryUI("output")
                    self.outputRunningHtml = gr.HTML(visible=False, elem_classes=["mcww-visible", "mcww-running-html"])
                    self.outputErrorMarkdown = gr.Markdown(visible=False, elem_classes=["mcww-visible", "mcww-project-error-md", "allow-pwa-select"])
                    self._makeCategoryUI("important")

