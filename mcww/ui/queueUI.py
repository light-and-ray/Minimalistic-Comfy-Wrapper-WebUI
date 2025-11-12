import json, uuid
import gradio as gr
from gradio.components.video import VideoData
from mcww import queueing, shared
from mcww.processing import Processing, ProcessingStatus
from mcww.utils import DataType, saveLogError
from mcww.ui.uiUtils import getMcwwLoaderHTML, showRenderingErrorGradio
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.comfyFile import ComfyFile, ImageData


class QueueUI:
    def __init__(self):
        self._entries: dict[int, Processing] = dict()
        self._entries_last_version: int = -1
        self._buildQueueUI()

    def _ensureEntriesUpToDate(self):
        if queueing.queue.getQueueVersion() <= self._entries_last_version:
            return
        self._entries_last_version = queueing.queue.getQueueVersion()
        values: list[Processing] = queueing.queue.getAllProcessings()
        self._entries = dict()
        for value in values:
            self._entries[value.id] = value


    @staticmethod
    def _getPauseButtonLabel():
        if queueing.queue.isPaused():
            return "▶"
        else:
            return "⏸"

    @staticmethod
    def _onTogglePause():
        queueing.queue.togglePause()
        return QueueUI._getPauseButtonLabel()

    @staticmethod
    def _getOnCancel(selectedId: int):
        def onCancel():
            queueing.queue.cancel(selectedId)
        return onCancel

    @staticmethod
    def _getOnRestart(selectedId: int):
        def onRestart():
            queueing.queue.restart(selectedId)
        return onRestart


    def _getQueueUIJson(self):
        data = dict()
        for key, value in self._entries.items():
            fileUrl: str|None = None
            for outputElement in value.outputElements:
                if isinstance(outputElement.value, list):
                    for listEntry in outputElement.value:
                        if isinstance(listEntry, ComfyFile):
                            fileUrl = listEntry.getUrl()
                            if listEntry.getDataType() == DataType.VIDEO:
                                thumbnailUrl = queueing.queue.getThumbnailUrlForVideoUrl(fileUrl)
                                if thumbnailUrl:
                                    fileUrl = thumbnailUrl
                            break
                if fileUrl: break
            if not fileUrl:
                for inputElement in value.inputElements:
                    if inputElement.element.category == "prompt":
                        if isinstance(inputElement.value, ImageData):
                            fileUrl = inputElement.value.url
                            break
                        if isinstance(inputElement.value, VideoData):
                            fileUrl = inputElement.value.video.url
                            thumbnailUrl = queueing.queue.getThumbnailUrlForVideoUrl(fileUrl)
                            if thumbnailUrl:
                                fileUrl = thumbnailUrl
                            break
            text = ""
            for inputElement in value.inputElements:
                if inputElement.element.category == "prompt":
                    if inputElement.value and isinstance(inputElement.value, str):
                        text += inputElement.value + '; '
            text = text.removesuffix('; ')
            data[key] = {
                "fileUrl" : fileUrl,
                "text" : text,
                "id" : key,
                "status" : value.status.value,
            }
        return json.dumps(data, indent=2)


    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui"], visible=False) as self.ui:
            refreshWorkflowTrigger = gr.Textbox(visible=False)
            refreshRadioTrigger = gr.Textbox(visible=False)
            with gr.Column(scale=15):
                pause = gr.Button(value=self._getPauseButtonLabel, scale=0,
                        elem_classes=["force-text-style"])
                pause.click(
                    fn=self._onTogglePause,
                    outputs=[pause],
                )
                radio = gr.Radio(
                    show_label=False,
                    elem_classes=["mcww-queue-radio", "mcww-hidden", "scroll-to-selected"],
                    value=-1,
                    choices=[-1])
                radio.select(
                    **shared.runJSFunctionKwargs("activateLoadingPlaceholder")
                ).then(
                    fn=lambda: str(uuid.uuid4()),
                    outputs=[refreshWorkflowTrigger],
                )
                radio.change(
                    **shared.runJSFunctionKwargs("scrollSelectedOnChange")
                )

                uiJson = gr.Textbox(interactive=False, elem_classes=["mcww-queue-json", "mcww-hidden"])
                uiJson.change(
                    **shared.runJSFunctionKwargs("applyMcwwQueueJson")
                )

                @gr.on(
                    triggers=[shared.webUI.load],
                    outputs=[refreshWorkflowTrigger, refreshRadioTrigger]
                )
                def onWebUILoadQueue():
                    return str(uuid.uuid4()), str(uuid.uuid4())

                @gr.on(
                    triggers=[refreshRadioTrigger.change],
                    inputs=[radio],
                    outputs=[radio, uiJson],
                    show_progress='hidden',
                )
                def onRefreshQueueRadio(selected):
                    self._ensureEntriesUpToDate()
                    radioChoices = [x for x in self._entries.keys()] + [-1]
                    if selected not in radioChoices:
                        selected = -1
                    radioUpdate = gr.Radio(
                        choices=radioChoices,
                        value=selected,
                    )
                    textboxUpdate = gr.Textbox(value=self._getQueueUIJson())
                    return radioUpdate, textboxUpdate



            with gr.Column(scale=15):
                @gr.render(
                    triggers=[refreshWorkflowTrigger.change],
                    inputs=[radio],
                )
                def renderQueueWorkflow(selected):
                    try:
                        currentSelectedEntryStatus: ProcessingStatus|None = None
                        selectedEntryId: int|None = None
                        self._ensureEntriesUpToDate()

                        if selected == -1 or not self._entries or not selected:
                            gr.Markdown("Nothing is selected", elem_classes=["active-workflow-ui"])

                        if selected in self._entries:
                            with gr.Row(elem_classes=["block-row-column"]):
                                moveUpButton = gr.Button("🡑", elem_classes=["mcww-tool"], scale=0)
                                moveUpButton.click(
                                    fn=lambda: queueing.queue.moveUp(selected),
                                ).then(
                                    fn=lambda: str(uuid.uuid4()),
                                    outputs=[refreshRadioTrigger],
                                )
                                moveDownButton = gr.Button("🡓", elem_classes=["mcww-tool"], scale=0)
                                moveDownButton.click(
                                    fn=lambda: queueing.queue.moveDown(selected),
                                ).then(
                                    fn=lambda: str(uuid.uuid4()),
                                    outputs=[refreshRadioTrigger],
                                )
                                cancelButton = gr.Button(value="⊘", variant="stop", scale=0,
                                        elem_classes=["force-text-style"], visible=False)
                                cancelButton.click(
                                    fn=self._getOnCancel(selected),
                                )
                                restartButton = gr.Button(value="⟳", scale=0,
                                        elem_classes=["force-text-style"], visible=False)
                                restartButton.click(
                                    fn=self._getOnRestart(selected),
                                )
                            entry = self._entries[selected]
                            if entry.status == ProcessingStatus.ERROR:
                                gr.Markdown(entry.error, elem_classes=["mcww-visible"])
                                restartButton.visible = True
                            elif entry.status in [ProcessingStatus.IN_PROGRESS, ProcessingStatus.QUEUED]:
                                cancelButton.visible = True
                            currentSelectedEntryStatus = entry.status
                            selectedEntryId = entry.id

                            workflowUI = WorkflowUI(
                                        workflow=entry.workflow,
                                        name=f'queued {selected}',
                                        mode=WorkflowUI.Mode.QUEUE)
                            for inputElementUI, inputElementProcessing in zip(
                                workflowUI.inputElements, entry.inputElements
                            ):
                                inputElementUI.gradioComponent.value = inputElementProcessing.value
                            if entry.status == ProcessingStatus.COMPLETE:
                                for outputElementUI, outputElementProcessing in zip(
                                    workflowUI.outputElements, entry.getOutputsForComponentInit()
                                ):
                                    outputElementUI.gradioComponent.value = outputElementProcessing

                        gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))

                        pullQueueUpdatesButton = gr.Button(json.dumps({
                                    "type": "queue",
                                    "oldVersion": queueing.queue.getQueueVersion(),
                                }),
                                elem_classes=["mcww-pull", "mcww-hidden"])

                        def onPullUpdatesClicked():
                            radioUpdate = str(uuid.uuid4())
                            workflowUpdate = gr.Textbox()
                            if selectedEntryId and currentSelectedEntryStatus != queueing.queue.getProcessing(selectedEntryId).status:
                                workflowUpdate = str(uuid.uuid4())
                            return workflowUpdate, radioUpdate

                        pullQueueUpdatesButton.click(
                            fn=onPullUpdatesClicked,
                            inputs=[],
                            outputs=[refreshWorkflowTrigger, refreshRadioTrigger],
                            show_progress="hidden",
                        ).then(
                            **shared.runJSFunctionKwargs("pullIsDone")
                        )

                    except Exception as e:
                        saveLogError(e, "Error on rendering queue workflow")
                        showRenderingErrorGradio(e)


