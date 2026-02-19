import json, uuid
from wrapt import synchronized
import gradio as gr
from gradio.components.gallery import GalleryData, GalleryImage, GalleryVideo
from gradio.components.video import VideoData
from mcww import queueing, shared
from mcww.comfy.nodeUtils import toGradioPayload
from mcww.processing import Processing, ProcessingStatus
from mcww.utils import DataType, saveLogError
from mcww.ui.uiUtils import getMcwwLoaderHTML, showRenderingErrorGradio
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.comfyFile import ComfyFile, ImageData, DataType


class QueueUI:
    def __init__(self):
        self._entries: dict[int, Processing] = dict()
        self._entries_last_version: int = -1
        self._buildQueueUI()

    @synchronized
    def _ensureEntriesUpToDate(self):
        currentVersion = queueing.queue.getQueueVersion()
        if currentVersion <= self._entries_last_version:
            return
        self._entries_last_version = currentVersion
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
            if queueing.queue.isPaused():
                gr.Info("Restarted, but queue is paused", 4)
        return onRestart

    @staticmethod
    def _getOnSkipBatchOne(selectedId: int):
        def onSkipBatchOne():
            processing = queueing.queue.getProcessing(selectedId)
            gr.Info("The batch task with the error was skipped", 4)
            processing.skipBatchOne()
            queueing.queue.restart(selectedId)
            if queueing.queue.isPaused():
                gr.Info("Skipped + restarted, but queue is paused", 4)
        return onSkipBatchOne

    @staticmethod
    def _alertQueuePausedOnUiLoad():
        if queueing.queue.isPaused():
            gr.Info("Queue is paused", 4)

    @synchronized
    def _getQueueUIJson(self):
        data = dict()
        for precessingId, entry in self._entries.items():
            fileUrl: str|None = None
            texts = list[str]()
            if entry.batchSizeTotal() > 1:
                texts.append(f"batch {entry.batchDone}/{entry.batchSizeTotal()}")
            for outputElement in entry.outputElements:
                if isinstance(outputElement.value, list):
                    for listEntry in outputElement.value:
                        if isinstance(listEntry, ComfyFile):
                            if listEntry.getDataType() not in (DataType.IMAGE, DataType.VIDEO):
                                continue
                            fileUrl = listEntry.getUrl()
                            if listEntry.getDataType() == DataType.VIDEO:
                                thumbnailUrl = queueing.queue.getThumbnailUrlForVideoUrl(fileUrl)
                                if thumbnailUrl:
                                    fileUrl = thumbnailUrl
                            break
                        elif isinstance(listEntry, str):
                            texts.append(listEntry)
                if fileUrl: break
            if not fileUrl:
                for mediaElement in entry.mediaElements:
                    for value in mediaElement.batchValues:
                        if isinstance(value, ImageData):
                            fileUrl = value.url
                        elif isinstance(value, VideoData):
                            fileUrl = value.video.url
                            thumbnailUrl = queueing.queue.getThumbnailUrlForVideoUrl(fileUrl)
                            if thumbnailUrl:
                                fileUrl = thumbnailUrl
                        elif isinstance(value, ComfyFile):
                            fileUrl = value.getUrl()
                            if value.getDataType() == DataType.VIDEO:
                                thumbnailUrl = queueing.queue.getThumbnailUrlForVideoUrl(fileUrl)
                                if thumbnailUrl:
                                    fileUrl = thumbnailUrl
                        if fileUrl: break
                    if fileUrl: break
            for inputElement in entry.inputElements:
                if inputElement.element.category == "prompt":
                    if inputElement.value and isinstance(inputElement.value, str):
                        texts.append(inputElement.value)

            texts.append(entry.workflowName)
            data[precessingId] = {
                "fileUrl" : fileUrl,
                "text" : '; '.join(texts),
                "id" : precessingId,
                "status" : entry.status.value,
            }
        return json.dumps(data, indent=2)


    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui", "mcww-key-queue"]) as self.ui:
            refreshWorkflowTrigger = gr.Textbox(visible=False)
            refreshRadioTrigger = gr.Textbox(visible=False)
            shared.webUI.load(fn=self._alertQueuePausedOnUiLoad)

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
                    **shared.runJSFunctionKwargs("afterQueueEntrySelected")
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
                    outputs=[radio, uiJson, pause],
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
                    uiJsonUpdate = gr.Textbox(value=self._getQueueUIJson())
                    return radioUpdate, uiJsonUpdate, QueueUI._getPauseButtonLabel()


            with gr.Column(scale=15, elem_classes=["workflow-ui-parent"]):
                @gr.render(
                    triggers=[refreshWorkflowTrigger.change],
                    inputs=[radio],
                )
                def renderQueueWorkflow(selected):
                    try:
                        currentSelectedEntryStatus: ProcessingStatus|None = None
                        selectedEntryId: int|None = None
                        self._ensureEntriesUpToDate()

                        if not queueing.queue.getProcessing(selected) or not self._entries or not selected:
                            gr.Markdown("Nothing is selected", elem_classes=["info-text", "workflow-ui"])

                        if selected in self._entries:
                            entry = self._entries[selected]
                            with gr.Row(elem_classes=["queue-control-row"], equal_height=True):
                                moveUpButton = gr.Button("🡑", elem_classes=["mcww-tool", "mcww-queue-move-up"], scale=0)
                                moveUpButton.click(
                                    fn=lambda: queueing.queue.moveUp(selected),
                                ).then(
                                    fn=lambda: str(uuid.uuid4()),
                                    outputs=[refreshRadioTrigger],
                                ).then(
                                    **shared.runJSFunctionKwargs("scrollToPreviousQueueEntry")
                                )
                                moveDownButton = gr.Button("🡓", elem_classes=["mcww-tool", "mcww-queue-move-down"], scale=0)
                                moveDownButton.click(
                                    fn=lambda: queueing.queue.moveDown(selected),
                                ).then(
                                    fn=lambda: str(uuid.uuid4()),
                                    outputs=[refreshRadioTrigger],
                                ).then(
                                    **shared.runJSFunctionKwargs("scrollToNextQueueEntry")
                                )
                                cancelButton = gr.Button(value="⊘", variant="stop", scale=0,
                                        elem_classes=["force-text-style"], visible=False)
                                cancelButton.click(
                                    fn=self._getOnCancel(selected),
                                )
                                restartButton = gr.Button(value="⭯", scale=0,
                                        elem_classes=["force-text-style"], visible=False)
                                restartButton.click(
                                    fn=self._getOnRestart(selected),
                                )
                                skipBatchOne = gr.Button("⥇", scale=0, visible=False, elem_classes=["mcww-tool"])
                                skipBatchOne.click(
                                    fn=self._getOnSkipBatchOne(selected),
                                )
                                gr.Markdown(entry.workflowName, elem_classes=["info-text", "vertically-centred", "allow-pwa-select",
                                                                                            "queue-workflow-name"])
                            if entry.status == ProcessingStatus.ERROR:
                                gr.Markdown(entry.error, elem_classes=["mcww-visible", "allow-pwa-select"])
                                restartButton.visible = True
                                if entry.batchSizeTotal() > 1 and entry.batchDone < entry.batchSizeTotal()-1:
                                    skipBatchOne.visible = True
                            elif entry.status in [ProcessingStatus.IN_PROGRESS, ProcessingStatus.QUEUED]:
                                cancelButton.visible = True
                            currentSelectedEntryStatus = entry.status
                            currentSelectedEntryBatchDone = entry.batchDone
                            selectedEntryId = entry.id

                            workflowUI = WorkflowUI(
                                        workflow=entry.workflow,
                                        name=f'queued {selected}',
                                        mode=WorkflowUI.Mode.QUEUE)
                            for inputElementUI, inputElementProcessing in zip(
                                workflowUI.inputElements, entry.inputElements
                            ):
                                value = inputElementProcessing.value
                                if isinstance(value, ComfyFile):
                                    value = value.getGradioInput()
                                inputElementUI.gradioComponent.value = value
                            for mediaBatchElementUI, mediaElementProcessing in zip(
                                workflowUI.mediaBatchElements, entry.mediaElements
                            ):
                                galleryRoot = []
                                for value in mediaElementProcessing.batchValues:
                                    value = toGradioPayload(value)
                                    if isinstance(value, ImageData):
                                        galleryRoot.append(GalleryImage(image=value))
                                    elif isinstance(value, VideoData):
                                        galleryRoot.append(GalleryVideo(video=value.video))
                                    elif isinstance(value, ComfyFile):
                                        gradioInput = value.getGradioInput()
                                        if value.getDataType() == DataType.IMAGE:
                                            galleryRoot.append(GalleryImage(image=gradioInput))
                                        else:
                                            galleryRoot.append(GalleryVideo(video=gradioInput.video))
                                mediaBatchElementUI.gradioComponent.value = GalleryData(root=galleryRoot)
                                if len(galleryRoot) <= 1:
                                    label = mediaBatchElementUI.gradioComponent.label
                                    mediaBatchElementUI.gradioComponent.label = label.removesuffix(" (batch)")
                            for outputElementUI, output in zip(
                                workflowUI.outputElements, entry.getOutputsForComponentInit()
                            ):
                                if isinstance(outputElementUI.gradioComponent, gr.Dataset):
                                    samples = output
                                    samplesLabels = [f"{x+1}" for x in range(len(samples))]
                                    tmp = gr.Dataset(samples=samples, sample_labels=samplesLabels, render=False)
                                    outputElementUI.gradioComponent.samples = tmp.samples
                                    outputElementUI.gradioComponent.sample_labels = tmp.sample_labels
                                    outputElementUI.gradioComponent.raw_samples = tmp.raw_samples
                                else:
                                    outputElementUI.gradioComponent.value = output

                            runningHtmlText = ""
                            if entry.status == ProcessingStatus.IN_PROGRESS:
                                runningHtmlText = 'Running<span class="running-dots"></span> '
                                if entry.batchSizeTotal() > 1:
                                    runningHtmlText += f"(batch: {entry.batchDone}/{entry.batchSizeTotal()} done) "
                            elif entry.status == ProcessingStatus.ERROR:
                                if entry.batchSizeTotal() > 1:
                                    runningHtmlText = f"Batch: {entry.batchDone}/{entry.batchSizeTotal()} done before the error or interruption"
                            if runningHtmlText:
                                workflowUI.outputRunningHtml.value = runningHtmlText
                                workflowUI.outputRunningHtml.visible = True
                            workflowUI.batchCountComponent.value = entry.batchSizeCount()

                        gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                        pullQueueUpdatesButton = gr.Button(json.dumps({
                                    "type": "queue",
                                    "oldVersion": self._entries_last_version,
                                }),
                                elem_classes=["mcww-pull", "mcww-hidden"])

                        def onPullUpdatesClicked():
                            radioUpdate = str(uuid.uuid4())
                            workflowUpdate = gr.Textbox()
                            processing = queueing.queue.getProcessing(selectedEntryId)
                            if not processing or selectedEntryId and not (currentSelectedEntryStatus == processing.status \
                                        and currentSelectedEntryBatchDone == processing.batchDone):
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
                        showRenderingErrorGradio(e, "Error on rendering queue workflow")


