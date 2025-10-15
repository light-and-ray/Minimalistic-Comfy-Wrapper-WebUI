from dataclasses import dataclass
from enum import Enum
import gradio as gr
from mcww import queueing
from mcww.comfyAPI import ComfyFile, ImageData
from mcww.processing import Processing
from mcww.workflowUI import WorkflowUI
from mcww.utils import getMcwwLoaderHTML, getRunJSFunctionKwargs
import json, uuid


class QueueUIEntryType(Enum):
    QUEUED = "queued"
    ERROR = "error"
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"


@dataclass
class QueueUIEntry:
    processing: Processing
    type: QueueUIEntryType


class QueueUI:
    def __init__(self, mainUIPageRadio: gr.Radio, webui: gr.Blocks):
        self._entries: dict[int, QueueUIEntry] = dict()
        self._entries_last_version: int = -1
        self.mainUIPageRadio = mainUIPageRadio
        self.webui = webui
        self._buildQueueUI()

    def _ensureEntriesUpToDate(self):
        if queueing.queue.getQueueVersion() <= self._entries_last_version:
            return
        self._entries_last_version = queueing.queue.getQueueVersion()
        values: list[QueueUIEntry] = []
        inProgress = queueing.queue.getInProgress()
        if inProgress:
            values.append(QueueUIEntry(processing=inProgress, type=QueueUIEntryType.IN_PROGRESS))
        for processingList, type in zip([
            queueing.queue.getQueueList(),
            queueing.queue.getErrorList(),
            queueing.queue.getCompleteList()],[
                QueueUIEntryType.QUEUED,
                QueueUIEntryType.ERROR,
                QueueUIEntryType.COMPLETE,
        ]):
            for processing in processingList:
                values.append(QueueUIEntry(
                    processing=processing,
                    type=type,
                ))
        values = sorted(values, key=lambda x: x.processing.id, reverse=True)
        self._entries = dict()
        for value in values:
            self._entries[value.processing.id] = value


    def _getPauseButtonLabel(self):
        if queueing.queue.isPaused():
            return "▶"
        else:
            return "⏸"

    def _onTogglePause(self):
        queueing.queue.togglePause()
        return self._getPauseButtonLabel()


    def _getQueueUIJson(self):
        data = dict()
        for key, value in self._entries.items():
            image: str|None = None
            for outputElement in value.processing.outputElements:
                if isinstance(outputElement.value, list):
                    for listEntry in outputElement.value:
                        if isinstance(listEntry, ComfyFile):
                            image = listEntry.getUrl()
                            break
                if image: break
            if not image:
                for inputElement in value.processing.inputElements:
                    if inputElement.element.category == "image_prompt":
                        if isinstance(inputElement.value, ImageData):
                            image = inputElement.value.url
                            break
            text = ""
            for inputElement in value.processing.inputElements:
                if inputElement.element.category == "text_prompt":
                    if inputElement.value and isinstance(inputElement.value, str):
                        text += inputElement.value + '; '
            text = text.removesuffix('; ')
            data[key] = {
                "image" : image,
                "text" : text,
                "id" : key,
                "type" : value.type.value,
            }
        return json.dumps(data, indent=2)


    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui"], visible=False) as queueUI:
            self.refreshWorkflowTrigger = gr.Textbox(visible=False)
            self.refreshRadioTrigger = gr.Textbox(visible=False)
            dummyComponent = gr.Textbox(visible=False)
            runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)
            with gr.Column(scale=15):
                self.radio = gr.Radio(
                    show_label=False,
                    elem_classes=["mcww-queue-radio", "mcww-hidden"],
                    value=-1,
                    choices=[-1])

                uiJson = gr.Textbox(interactive=False, elem_classes=["mcww-queue-json", "mcww-hidden"])
                uiJson.change(
                    **runJSFunctionKwargs("applyMcwwQueueJson")
                )

                @gr.on(
                    triggers=[self.mainUIPageRadio.change, self.webui.load],
                    outputs=[self.refreshWorkflowTrigger, self.refreshRadioTrigger]
                )
                def _():
                    return str(uuid.uuid4()), str(uuid.uuid4())

                @gr.on(
                    triggers=[self.refreshRadioTrigger.change],
                    inputs=[self.radio, self.mainUIPageRadio],
                    outputs=[self.radio, uiJson, queueUI],
                    show_progress='hidden',
                )
                def _(selected, mainUIPage):
                    if mainUIPage != "queue":
                        return gr.Radio(), gr.Textbox(), gr.Row(visible=False)
                    self._ensureEntriesUpToDate()
                    radioChoices = [x for x in self._entries.keys()] + [-1]
                    if selected not in radioChoices:
                        selected = -1
                    radioUpdate = gr.Radio(
                        choices=radioChoices,
                        value=selected,
                    )
                    textboxUpdate = gr.Textbox(value=self._getQueueUIJson())
                    return radioUpdate, textboxUpdate, gr.Row(visible=True)

                self.radio.select(
                    **runJSFunctionKwargs("activateLoadingPlaceholder")
                ).then(
                    fn=lambda: str(uuid.uuid4()),
                    outputs=[self.refreshWorkflowTrigger],
                )


            with gr.Column(scale=15):
                pause = gr.Button(value=self._getPauseButtonLabel(), elem_classes=["force-text-style"])
                pause.click(
                    fn=self._onTogglePause,
                    outputs=[pause],
                )
                @gr.render(
                    triggers=[self.mainUIPageRadio.change, self.refreshWorkflowTrigger.change],
                    inputs=[self.radio, self.mainUIPageRadio],
                )
                def _(selected, mainUIPage: str):
                    if mainUIPage != "queue": return

                    pullQueueUpdatesButton = gr.Button("Pull queue updates",
                            elem_classes=["mcww-pull", "mcww-hidden"])
                    pullQueueUpdatesButton.click(
                        fn=queueing.queue.getOnPullQueueUpdates(queueing.queue.getQueueVersion()),
                        inputs=[],
                        outputs=[self.refreshWorkflowTrigger, self.refreshRadioTrigger],
                        show_progress="hidden",
                    )
                    self._ensureEntriesUpToDate()

                    if selected == -1 or not self._entries or not selected:
                        gr.Markdown("Nothing is selected", elem_classes=["active-workflow-ui"])

                    if selected in self._entries:
                        entry = self._entries[selected]
                        if entry.type == QueueUIEntryType.ERROR:
                            gr.Markdown(entry.processing.error, elem_classes=["mcww-visible"])

                        workflowUI = WorkflowUI(
                                    workflow=entry.processing.workflow,
                                    name=f'queued {selected}',
                                    needResizableRow=False)
                        workflowUI.runButton.visible = False
                        for inputElementUI, inputElementProcessing in zip(
                            workflowUI.inputElements, entry.processing.inputElements
                        ):
                            inputElementUI.gradioComponent.interactive = False
                            inputElementUI.gradioComponent.value = inputElementProcessing.value
                        if entry.type == QueueUIEntryType.COMPLETE:
                            for outputElementUI, outputElementProcessing in zip(
                                workflowUI.outputElements, entry.processing.getOutputsForComponentInit()
                            ):
                                outputElementUI.gradioComponent.value = outputElementProcessing

                    gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))


