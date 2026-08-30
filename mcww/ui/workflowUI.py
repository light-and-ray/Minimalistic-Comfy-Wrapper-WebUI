from dataclasses import dataclass
from enum import Enum
import gradio as gr
from gradio import FileData
import uuid, os
from mcww import queueing, shared, opts
from mcww.comfy.comfyFile import ComfyFile
from mcww.utils import DataType
from mcww.ui.presetsWorkflowUI import renderPresetsInWorkflowUI
from mcww.ui.uiUtils import ( renderHolidaySpecial, JsonTextbox, MCWWMarkdown, getFixTabsElementIdSource,
    getFixTabsElementIdTarget, getARPreview
)
from mcww.comfy.workflow import Element, DummyElement, Workflow


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

    def __init__(self, workflow: Workflow, name, mode: Mode, pullOutputsKey: str|None = None,
                                queueModePresetsBatch: bool = False):
        self.name = name
        self.pullOutputsKey = pullOutputsKey
        self.inputElements: list[ElementUI] = []
        self.outputElements: list[ElementUI] = []
        self.selectedMediaTabComponent: gr.Textbox = None
        self.presetsBatchModeComponent: gr.Checkbox = None
        self.mediaSingleElements: list[ElementUI] = []
        self.mediaBatchElements: list[ElementUI] = []
        self.textPromptElements: list[ElementUI] = []
        self.presetsBatchDropdownElement: ElementUI = None
        self.workflow = workflow
        self.outputRunningHtml: gr.HTML = None
        self.outputErrorMarkdown: gr.Markdown = None
        self.batchCountComponent: gr.Number = None
        self.priorityComponent: gr.Number = None
        self.applyNewPriorityButton: gr.Button = None
        self._queueModePresetsBatch = queueModePresetsBatch
        self._hasSeed = False
        self._otherWidthHeight: dict[str, gr.Number] = {}
        self._mode = mode
        self._buildWorkflowUI()


    def _makeInputElementUI(self, element: Element, promptType: str):
        minMaxStep = element.parseMinMaxStep()
        showDefault = element.showDefault() or self._mode == self.Mode.METADATA

        if element.field.type == DataType.IMAGE:
            component = gr.Image(label=element.label, type="pil", show_download_button=True, render=False)
            component.webcam_options.mirror = opts.options.mirrorWebCamera
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
        elif element.field.type == DataType.BOOLEAN:
            component = gr.Checkbox(value=element.field.defaultValue, label=element.label, render=False)
        elif element.field.type == DataType.NOTE:
            component = MCWWMarkdown(value=element.field.defaultValue, elem_classes=["allow-pwa-select"], render=False)
            if len(element.field.defaultValue) > opts.options.noteLengthCollapseLimit:
                with gr.Accordion(open=False, label=element.label, elem_classes=["mcww-pseudo-gallery", "need-save-state", "accordion"]):
                    component.render()
            else:
                with gr.Group(elem_classes=["mcww-pseudo-gallery"]):
                    gr.Markdown(value=element.label, elem_classes=["mcww-visible", "info-text", "markdown-label"])
                    component.render()
            return
        elif element.field.type == DataType.VIDEO:
            component = gr.Video(label=element.label, loop=True,
                            show_download_button=True, render=False, elem_classes=["mcww-other-gallery", "no-compare"])
            component.webcam_options.mirror = opts.options.mirrorWebCamera
        elif element.field.type == DataType.AUDIO:
            component = gr.Audio(label=element.label, render=False,
                            show_download_button=True, elem_classes=["mcww-other-gallery", "no-compare", "reupload-on-workflow-rendered"])
        else:
            gr.Markdown(value=f"Not yet implemented [{element.field.type}]: {element.label}")
            return

        if element.isSeed():
            self._hasSeed = True

        if self._mode == self.Mode.PROJECT and element.isSeed():
            with gr.Row(elem_classes=["vertically-centred"]):
                component.render()
                component.value = -1
                randomButton = gr.Button(value="🎲", elem_classes=["mcww-tool"])
                randomButton.click(fn=lambda: -1, outputs=[component])
                reuseButton = gr.Button(value="♻️", elem_classes=["mcww-tool"])
                reuseButton.click(
                    fn=queueing.queue.getOnPullPreviousUsedSeed(self.pullOutputsKey, element.getKey()),
                    outputs=[component])

        elif element.isWidth() or element.isHeight():
            widthHeightKey = element.label.lower().replace("width", "").replace("height", "")
            if not self._otherWidthHeight.get(widthHeightKey):
                component.render()
                self._otherWidthHeight[widthHeightKey] = component
            else:
                if element.isWidth():
                    width = component
                    height = self._otherWidthHeight[widthHeightKey]
                else:
                    width = self._otherWidthHeight[widthHeightKey]
                    height = component

                self._otherWidthHeight[widthHeightKey].unrender()
                self._otherWidthHeight[widthHeightKey] = None

                with gr.Row(elem_classes=["vertically-centred", "mcww-other-gallery"]):
                    with gr.Column(min_width=200):
                        width.render()
                        height.render()
                        arPreview = gr.Image(
                                format="png", show_label=False, show_download_button=False, show_fullscreen_button=False,
                                elem_classes=["no-copy", "no-compare", "aspect-ratio-preview", "no-pwa-context-menu"])
                        gr.on(
                            triggers=[width.change, height.change],
                            fn=getARPreview,
                            inputs=[width, height],
                            outputs=[arPreview],
                            show_progress="hidden",
                            preprocess=False,
                        )
                    if self._mode == self.Mode.PROJECT:
                        swapButton = gr.Button(value="🔃", elem_classes=["mcww-tool", "force-emoji", "swap-resolution"])
                        fromClipboardButton = gr.Button(value="📋", elem_classes=["mcww-tool", "force-emoji", "paste"])
                        swapButton.click(
                            fn=lambda x, y: (y, x),
                            inputs=[width, height],
                            outputs=[width, height],
                            preprocess=False,
                            postprocess=False,
                        )
                        def afterGetWidthHeightFromClipboardMedia(width, height):
                            width = int(width) if width else gr.update()
                            height = int(height) if height else gr.update()
                            return width, height
                        fromClipboardButton.click(
                            fn=afterGetWidthHeightFromClipboardMedia,
                            inputs=[shared.dummyComponent, shared.dummyComponent],
                            outputs=[width, height],
                            js="getWidthHeightFromClipboardMedia",
                        )

        elif element.field.type == DataType.IMAGE and self._mode == self.Mode.PROJECT:
            with gr.Column(elem_classes=["input-image-column", f"mcww-key-{str(uuid.uuid4())}"]):
                component.render()
                with gr.Row(elem_classes=["right-aligned"]):
                    returnButton = gr.Button("Return 🡒", visible=False, elem_classes=["mcww-text-button", "small-button", "return-button"])
                    gr.Button("Open in editor", elem_classes=["open-in-image-editor-button", "mcww-text-button", "small-button"])
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
        if promptType == "mediaSingle":
            self.mediaSingleElements.append(elementUI)
        elif promptType == "text":
            self.textPromptElements.append(elementUI)
        else:
            self.inputElements.append(elementUI)

        if element.field.type in (DataType.IMAGE, DataType.VIDEO, DataType.AUDIO):
            if showDefault and isinstance(element.field.defaultValue, ComfyFile):
                component.value = element.field.defaultValue.getGradioInputForComponentInit()
        return elementUI


    def _makeMediaBatchElementUI(self, element: Element):
        label = label=f'{element.label} (batch)'
        if element.field.type in [DataType.IMAGE, DataType.VIDEO]:
            elem_classes = ["gallery-workflow-fix-grid-height"]
            if self._mode == self.Mode.PROJECT:
                elem_classes.append("upload-gallery")
            if element.field.type == DataType.VIDEO:
                elem_classes.append("no-compare")
            component = gr.Gallery(label=label, elem_classes=elem_classes)
        else:
            viewComponent = gr.Audio(label=element.label, interactive=False, render=False,
                                show_download_button=True, elem_classes=["no-compare", "audio-container"])
            component = self._makeInputPseudoGallery(viewComponent, element, label)

        if self._mode in [self.Mode.QUEUE, self.Mode.METADATA]:
            component.interactive = False
        elementUI = ElementUI(element=element, gradioComponent=component, extraKey="mediaBatch")
        self.mediaBatchElements.append(elementUI)
        return elementUI


    def _makeInputPseudoGallery(self, viewComponent: gr.Component, element: Element, label: str):
        inputComponent = gr.Files(label=label, render=False, elem_classes=["upload-gallery", "input-component", "reupload-on-workflow-rendered"])
        previewGallery = self._makePseudoGallery(viewComponent, element, inputComponent)
        def onChange(files):
            if not files:
                return gr.Dataset(samples=[], sample_labels=[])
            labels = [str(i) for i in range(1, len(files)+1)]
            samples = []
            for file in files:
                url = f"/gradio_api/file={file}"
                name = os.path.basename(file)
                audio = FileData(path=file, url=url, orig_name=name, mime_type="audio")
                samples.append(audio)
            return gr.Dataset(samples=samples, sample_labels=labels)
        inputComponent.change(
            fn=onChange,
            inputs=[inputComponent],
            outputs=[previewGallery],
        ).then(
            **shared.runJSFunctionKwargs([
                "selectProperElementInPseudoGalleries",
                "updateOverflowGallerySelectedStyles",
            ])
        )
        return inputComponent


    def _makePseudoGallery(self, viewComponent: gr.Component, element: Element, _inputComponent: gr.Component = None):
        elem_classes = ["mcww-pseudo-gallery", "mcww-other-gallery", "no-compare"]
        if isinstance(viewComponent, gr.Textbox):
            elem_classes += ["no-open", "no-copy"]
        with gr.Group(elem_classes=elem_classes):
            originalLabel = viewComponent.label
            if _inputComponent and self._mode == self.Mode.PROJECT:
                originalLabel = "Preview"
            selectedIndex = gr.Textbox(container=False, elem_classes=["mcww-hidden", "selected-index"])
            labelHiddenComponent = gr.Textbox(visible=False)
            if not viewComponent.elem_classes:
                viewComponent.elem_classes = []
            viewComponent.elem_classes += ["view-component"]
            viewComponent.render()
            if isinstance(viewComponent, gr.Textbox):
                emptyMdValue = "```\n\n```\n"
                markdownByDefault = element.isMarkdown()
                viewComponent.visible = not markdownByDefault
                markdownViewLabel = gr.Markdown(value=originalLabel, visible=markdownByDefault, elem_classes=["mcww-visible", "info-text", "markdown-label"])
                elem_classes = ["allow-pwa-select"]
                if opts.options.protectUrlsInMarkdownOutput:
                    elem_classes.append("mcww-protect-links")
                markdownView = MCWWMarkdown(value=emptyMdValue, visible=markdownByDefault, elem_classes=elem_classes)
                @gr.on(triggers=[viewComponent.change],
                    inputs=[viewComponent, labelHiddenComponent],
                    outputs=[markdownView, markdownViewLabel],
                )
                def onViewComponentChange(text: str, label: str):
                    if not text:
                        text = emptyMdValue
                    return text, label

                with gr.Row():
                    showMarkdown = gr.Checkbox(value=markdownByDefault, label="Markdown", elem_classes=["mcww-tiny-element", "markdown-toggle"])
                    @gr.on(triggers=[showMarkdown.change],
                        inputs=[showMarkdown],
                        outputs=[viewComponent, markdownViewLabel, markdownView],
                    )
                    def onShowMarkdownChange(value: bool):
                        return gr.Textbox(visible=not value), gr.Markdown(visible=value), gr.Markdown(visible=value)

                    getFileName = lambda isMarkdown: f"{self.name}.md" if isMarkdown else f"{self.name}.txt"
                    fileNameComponent = gr.Textbox(value=getFileName(markdownByDefault), visible=False)
                    showMarkdown.change(
                        fn=getFileName,
                        inputs=[showMarkdown],
                        outputs=[fileNameComponent],
                    )
                    downloadTextButton = gr.Button("Download", elem_classes=["mcww-text-button", "download-text", "small-button", "info-text"], scale=0)
                    downloadTextButton.click(
                        fn=lambda x, y, z, w: None,
                        inputs=[showMarkdown, viewComponent, markdownView, fileNameComponent],
                        js="downloadTextOutput",
                    )

            galleryComponent = gr.Dataset(show_label=False, samples_per_page=99999, components=[shared.dummyComponent],
                                                elem_classes=["dataset"], type="tuple")
            if _inputComponent:
                _inputComponent.render()

            def onView(selectData: gr.SelectData):
                label = originalLabel
                samples = selectData.target.raw_samples
                selectedSampleLabel = selectData.target.sample_labels[selectData.index]
                if len(samples) > 1 or (len(samples) > 0 and selectedSampleLabel != "1"):
                    label = f"{originalLabel} #{selectedSampleLabel}"
                viewUpdate = gr.update(value=samples[selectData.index], label=label)
                indexUpdate = gr.Textbox(value=str(selectData.index))
                return viewUpdate, indexUpdate, label
            galleryComponent.select(
                fn=onView,
                inputs=[],
                outputs=[viewComponent, selectedIndex, labelHiddenComponent],
                postprocess=False,
                show_progress="hidden",
            ).then(
                **shared.runJSFunctionKwargs("updatePseudoGallerySelectedStyles")
            )
        return galleryComponent


    def _makeOutputElementUI(self, element: Element):
        with gr.Column(elem_classes=["overflow-gallery"]):
            if element.field.type in (DataType.IMAGE, DataType.VIDEO):
                elem_classes = []
                if element.field.type == DataType.VIDEO:
                    elem_classes += ["no-compare"]
                galleryComponent = gr.Gallery(label=element.label, interactive=False, elem_classes=elem_classes)
            elif element.field.type in (DataType.AUDIO, DataType.STRING):
                if element.field.type == DataType.AUDIO:
                    viewComponent = gr.Audio(label=element.label, interactive=False, render=False,
                                        show_download_button=True, elem_classes=["no-compare", "audio-container"])
                else: # DataType.STRING
                    viewComponent = gr.Textbox(label=element.label, interactive=False, render=False,
                                    lines=4, max_lines=20, show_copy_button=True)
                galleryComponent = self._makePseudoGallery(viewComponent, element)
            else:
                gr.Markdown(value=f"Not yet implemented [{element.field.type}]: {element.label}")
                return

            selectedIndex = gr.Textbox(container=False, elem_classes=["mcww-hidden", "overflow-gallery-selected-index"])
            outputGroupsDataset = gr.Dataset(show_label=True, samples_per_page=99999, components=[shared.dummyComponent],
                    label=f"{element.label} - overflow groups", elem_classes=["overflow-gallery-dataset"], type="tuple")
        originalLabel = element.label
        def onSelect(selectData: gr.SelectData):
            samples = selectData.target.raw_samples
            label = originalLabel
            if len(samples) > 1:
                label = f"{originalLabel} #{selectData.target.sample_labels[selectData.index]}"
            value = samples[selectData.index]
            if isinstance(galleryComponent, gr.Dataset):
                labels = [f"{selectData.index*opts.options.overflowGalleryGroupSize + x+1}" for x in range(len(value))]
                viewUpdate = gr.Dataset(samples=value, sample_labels=labels)
            else:
                viewUpdate = gr.update(value=value, label=label)
            indexUpdate = gr.Textbox(value=str(selectData.index))
            return viewUpdate, indexUpdate
        selectDependency = outputGroupsDataset.select(
            fn=onSelect,
            inputs=[],
            outputs=[galleryComponent, selectedIndex],
            postprocess=False,
            show_progress="hidden",
        ).then(
            **shared.runJSFunctionKwargs("updateOverflowGallerySelectedStyles")
        )
        if isinstance(galleryComponent, gr.Dataset):
            selectDependency.then(
                **shared.runJSFunctionKwargs([
                    "selectProperElementInPseudoGalleries",
                    "updateOverflowGallerySelectedStyles",
                ])
            )
        self.outputElements.append(ElementUI(element=element, gradioComponent=outputGroupsDataset))


    def _getAllowedForPromptType(self, promptType: str):
        if promptType.startswith("media"):
            allowed: list = [DataType.IMAGE, DataType.VIDEO, DataType.AUDIO]
        elif promptType == "text":
            allowed: list = [DataType.STRING]
        elif promptType == "other":
            allowed: list = [DataType.FLOAT, DataType.INT, DataType.NOTE]
        else:
            raise Exception("Can't be here")
        return allowed


    def _makeCategoryTabUI(self, category: str, tab: str, promptType: str|None):
        elements = self.workflow.getElementsRows(category, tab)
        if promptType:
            allowedTypes = self._getAllowedForPromptType(promptType)
            elements = [
                filtered_row for row in elements
                if (filtered_row := [element for element in row if element.field.type in allowedTypes])
            ]

        for elementsRow in elements:
            with gr.Row() if elementsRow else None:
                for element in elementsRow:
                    if category == "output":
                        self._makeOutputElementUI(element)
                    elif category == "prompt":
                        if promptType in ["mediaSingle", "text", "other"]:
                            element = self._makeInputElementUI(element, promptType)
                        elif promptType == "mediaBatch":
                            element = self._makeMediaBatchElementUI(element)

                        if element and promptType in ["mediaSingle", "mediaBatch"]:
                            if len(elements) == 1:
                                if hasattr(element.gradioComponent, "height"):
                                    element.gradioComponent.height = "min(80vh, 500px)"
                            else:
                                if hasattr(element.gradioComponent, "height"):
                                    element.gradioComponent.height = "min(80vh, 350px)"
                                if not element.gradioComponent.elem_classes:
                                    element.gradioComponent.elem_classes = []
                                element.gradioComponent.elem_classes.append("collapse-if-empty")
                    else:
                        self._makeInputElementUI(element, promptType)


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
        with gr.Column(elem_classes=[]) as categoryUI:
            if len(tabs) == 1:
                self._makeCategoryTabUI(category, tabs[0], promptType)
            else:
                tabsClasses = ["need-save-state"]
                if category == "prompt" and promptType.startswith("media"):
                    tabsClasses.append("project-media-prompt-tabs")
                    tabsClasses.append(f"{self._mode.value}-{promptType}")
                with gr.Tabs(elem_classes=tabsClasses):
                    firstTab = tabs[0]
                    restTabs = tabs[1:]
                    with gr.Tab(firstTab) as tabComponent:
                        self._makeCategoryTabUI(category, firstTab, promptType)
                        for tab in restTabs:
                            with gr.Column(elem_id=getFixTabsElementIdSource(f"{promptType}-{tab}"), elem_classes=["mcww-hidden"]):
                                self._makeCategoryTabUI(category, tab, promptType)
                    for tab in restTabs:
                        with gr.Tab(tab) as tabComponent:
                            with gr.Column(elem_id=getFixTabsElementIdTarget(f"{promptType}-{tab}")):
                                pass
        if category == "prompt" and promptType == "text":
            queueShowPresets = self._mode == self.Mode.QUEUE and self._queueModePresetsBatch
            if self._mode == self.Mode.PROJECT or queueShowPresets:
                with gr.Column(elem_classes=[]) as presetsBatchUI:
                    self.presetsBatchDropdownElement.gradioComponent.render()
                    with gr.Row(elem_classes=["floating-row", "right-aligned"], equal_height=True):
                        selectAllButton = gr.Button("Fill with everything", elem_classes=["mcww-text-button", "small-button", "info-text"])
            if queueShowPresets:
                categoryUI.visible = False
                self.presetsBatchDropdownElement.gradioComponent.interactive = False
                self.presetsBatchDropdownElement.gradioComponent.elem_classes.append("allow-pwa-select")
                selectAllButton.visible = False
            if self._mode == self.Mode.PROJECT:
                categoryUI.elem_id = "textCategoryUI"
                presetsBatchUI.elem_id = "presetsBatchUI"
                self.presetsBatchModeComponent.change(
                    fn=lambda x: None, # in python this doesn't work due to gradio bug
                    inputs=[self.presetsBatchModeComponent],
                    js="onSelectedPresetsBatchModeChange"
                )
                renderPresetsInWorkflowUI(self.name, self.textPromptElements, selectAllButton,
                    self.presetsBatchDropdownElement.gradioComponent, self.presetsBatchModeComponent,
                    presetsBatchUI, categoryUI)


    def _buildWorkflowUI(self):
        uiClasses = ["workflow-ui"]
        uiRowClasses = []
        if self._mode in [self.Mode.PROJECT]:
            uiRowClasses.append("resize-handle-row")
            uiRowClasses.append(f"mcww-key-workflow-{self.pullOutputsKey}")
        accordionsOpen = self._mode in [self.Mode.METADATA] or opts.options.openAccordionsAutomatically
        renderHolidaySpecial()
        with gr.Column(elem_classes=uiClasses):
            with gr.Row(elem_classes=uiRowClasses):
                with gr.Column(scale=15):
                    _presetsBatchDropdown = gr.Dropdown(render=False, label="Selected presets", multiselect=True,
                        allow_custom_value=True, choices=[], elem_classes=["only-remove-dropdown", "presets-batch-dropdown"])
                    self.presetsBatchDropdownElement = ElementUI(gradioComponent=_presetsBatchDropdown,
                                        element=DummyElement(), extraKey="presetsBatchDropdown")
                    self.presetsBatchModeComponent = gr.Checkbox(value=False, label="Presets batch mode", render=False, elem_classes=["need-save-state", "checkbox"])
                    self._makeCategoryUI("prompt", "text")

                    if self._mode == self.Mode.PROJECT and opts.options.showRunButtonCopy:
                        runButtonCopy = gr.Button("Run")
                        runButtonCopy.click(
                            **shared.runJSFunctionKwargs("onRunButtonCopyClick")
                        )

                    if self.workflow.categoryExists("advanced"):
                        with gr.Accordion("Advanced options", open=accordionsOpen, elem_classes=["need-save-state", "accordion"]):
                            self._makeCategoryUI("advanced")

                    self.selectedMediaTabComponent = gr.Textbox(visible=False, value="tabSingle")
                    if self._mode == self.Mode.PROJECT:
                        with gr.Tabs(elem_classes="need-save-state") as mediaCategoryUI:
                            with gr.Tab("Media single") as tabSingle:
                                self._makeCategoryUI("prompt", "mediaSingle")
                                with gr.Column(elem_id=getFixTabsElementIdSource("mediaBatch"), elem_classes=["mcww-hidden"]):
                                    self._makeCategoryUI("prompt", "mediaBatch")
                                    if len(self.mediaBatchElements) > 1:
                                        gr.Markdown("When there are more than 1 inputs for batch mode, the biggest list "
                                            "of files will be used and the smaller will repeat",
                                                elem_classes=["mcww-visible", "info-text", "media-batch-multi-inputs-info"])
                            with gr.Tab("Media batch", elem_id=getFixTabsElementIdTarget("mediaBatch")) as tabBatch:
                                pass
                            tabSingle.select(fn=lambda: "tabSingle", outputs=[self.selectedMediaTabComponent])
                            tabBatch.select(fn=lambda: "tabBatch", outputs=[self.selectedMediaTabComponent])
                        if len(self.mediaSingleElements) == 0:
                            mediaCategoryUI.visible = False
                    elif self._mode == self.Mode.METADATA:
                        self._makeCategoryUI("prompt", "mediaSingle")
                    elif self._mode == self.Mode.QUEUE:
                        self._makeCategoryUI("prompt", "mediaBatch")
                    self._makeCategoryUI("prompt", "other")
                    for customCategory in self.workflow.getCustomCategories():
                        with gr.Accordion(label=customCategory, open=accordionsOpen, elem_classes=["need-save-state", "accordion"]):
                            self._makeCategoryUI(customCategory)
                    if self._mode == self.Mode.METADATA:
                        self._makeCategoryUI("important")
                if self._mode in [self.Mode.QUEUE, self.Mode.PROJECT]:
                    with gr.Column(scale=15):
                        self._makeCategoryUI("output")
                        self.outputRunningHtml = gr.HTML(visible=False, elem_classes=["mcww-visible", "mcww-running-html"])
                        self.outputErrorMarkdown = gr.Markdown(visible=False, elem_classes=["mcww-visible", "mcww-error-md", "allow-pwa-select"])
                        self._makeCategoryUI("important")
                        with gr.Row(elem_classes=["right-aligned"]):
                            priorityVisible = opts.options.queueMaxPriority > 1
                            if self._mode == self.Mode.QUEUE:
                                self.applyNewPriorityButton = gr.Button("Apply new priority", elem_classes=["mcww-text-button", "small-button"],
                                                            scale=0, visible=priorityVisible)
                            self.priorityComponent = gr.Number(label="Priority", value=opts.options.defaultPriority, minimum=1, maximum=opts.options.queueMaxPriority,
                                visible=priorityVisible, elem_classes=["mcww-project-priority", "mcww-tiny-element"], precision=0)
                            batchCountVisible = self._hasSeed
                            if opts.options.forceShowBatchCount:
                                batchCountVisible = True
                            self.batchCountComponent = gr.Number(label="Batch count", value=1, minimum=1, visible=batchCountVisible,
                                            elem_classes=["mcww-batch-count-number", "mcww-tiny-element"], precision=0)
            gr.Textbox(elem_classes=["mcww-hidden", "mcww-workflow-rendered-trigger"], container=False)

