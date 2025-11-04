import json, uuid
import gradio as gr
from gradio.components.video import VideoData
from mcww import queueing
from mcww.processing import Processing, ProcessingType
from mcww.utils import DataType, saveLogError
from mcww.ui.uiUtils import getMcwwLoaderHTML, getRunJSFunctionKwargs, showRenderingErrorGradio
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.comfyFile import ComfyFile, ImageData


class QueueUI:
    def __init__(self, webUI: gr.Blocks):
        self._entries: dict[int, Processing] = dict()
        self._entries_last_version: int = -1
        self.webUI = webUI
        self._buildQueueUI()

    def _ensureEntriesUpToDate(self):
        if queueing.queue.getQueueVersion() <= self._entries_last_version:
            return
        self._entries_last_version = queueing.queue.getQueueVersion()
        values: list[Processing] = queueing.queue.getAllProcessings()
        values = sorted(values, key=lambda x: x.id, reverse=True)
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
    def _onInterrupt():
        queueing.queue.interrupt()
        gr.Info("Interrupting...", 3)

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
                "type" : value.type.value,
            }
        return json.dumps(data, indent=2)


    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui"], visible=False) as self.ui:
            refreshWorkflowTrigger = gr.Textbox(visible=False)
            refreshRadioTrigger = gr.Textbox(visible=False)
            dummyComponent = gr.Textbox(visible=False)
            runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)
            with gr.Column(scale=15):
                radio = gr.Radio(
                    show_label=False,
                    elem_classes=["mcww-queue-radio", "mcww-hidden", "need-see-selected"],
                    value=-1,
                    choices=[-1])

                uiJson = gr.Textbox(interactive=False, elem_classes=["mcww-queue-json", "mcww-hidden"])
                uiJson.change(
                    **runJSFunctionKwargs("applyMcwwQueueJson")
                )

                @gr.on(
                    triggers=[self.webUI.load],
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

                radio.select(
                    **runJSFunctionKwargs("activateLoadingPlaceholder")
                ).then(
                    fn=lambda: str(uuid.uuid4()),
                    outputs=[refreshWorkflowTrigger],
                )


            with gr.Column(scale=15):
                @gr.render(
                    triggers=[refreshWorkflowTrigger.change],
                    inputs=[radio],
                )
                def renderQueueWorkflow(selected):
                    try:
                        with gr.Row():
                            pause = gr.Button(value=self._getPauseButtonLabel(), scale=0,
                                    elem_classes=["force-text-style"])
                            pause.click(
                                fn=self._onTogglePause,
                                outputs=[pause],
                            )
                            interrupt = gr.Button(value="□", variant="stop", scale=0,
                                    elem_classes=["force-text-style"])
                            interrupt.click(
                                fn=self._onInterrupt,
                            )
                            restartButton = gr.Button(value="⟳", scale=0,
                                    elem_classes=["force-text-style"])
                            restartButton.click(
                                fn=self._getOnRestart(selected),
                            )

                        pullQueueUpdatesButton = gr.Button(json.dumps({
                                    "type": "queue",
                                    "oldVersion": queueing.queue.getQueueVersion(),
                                }),
                                elem_classes=["mcww-pull", "mcww-hidden"])
                        pullQueueUpdatesButton.click(
                            fn=lambda: (str(uuid.uuid4()), str(uuid.uuid4())),
                            inputs=[],
                            outputs=[refreshWorkflowTrigger, refreshRadioTrigger],
                            show_progress="hidden",
                        )
                        self._ensureEntriesUpToDate()

                        if selected == -1 or not self._entries or not selected:
                            gr.Markdown("Nothing is selected", elem_classes=["active-workflow-ui"])

                        if selected in self._entries:
                            entry = self._entries[selected]
                            if entry.type == ProcessingType.ERROR:
                                gr.Markdown(entry.error, elem_classes=["mcww-visible"])

                            workflowUI = WorkflowUI(
                                        workflow=entry.workflow,
                                        name=f'queued {selected}',
                                        mode=WorkflowUI.Mode.QUEUE)
                            for inputElementUI, inputElementProcessing in zip(
                                workflowUI.inputElements, entry.inputElements
                            ):
                                inputElementUI.gradioComponent.value = inputElementProcessing.value
                            if entry.type == ProcessingType.COMPLETE:
                                for outputElementUI, outputElementProcessing in zip(
                                    workflowUI.outputElements, entry.getOutputsForComponentInit()
                                ):
                                    outputElementUI.gradioComponent.value = outputElementProcessing

                        gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))

                    except Exception as e:
                        saveLogError(e, "Error on rendering queue workflow")
                        showRenderingErrorGradio(e)


