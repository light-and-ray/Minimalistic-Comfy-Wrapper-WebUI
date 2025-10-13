from dataclasses import dataclass
from enum import Enum
import gradio as gr
from mcww import queueing
from mcww.comfyAPI import ComfyFile, ImageData
from mcww.processing import Processing
from mcww.workflowUI import WorkflowUI
import json


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
    def __init__(self, selected: int):
        self._entries: dict[int, QueueUIEntry] = dict()
        self._selected = selected
        self._prepareEntries()
        self._buildQueueUI()

    def _prepareEntries(self):
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
                            image = listEntry.getDirectLink()
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
                        text += inputElement.value + ';'
            text = text.removesuffix(';')
            data[key] = {
                "image" : image,
                "text" : text,
                "id" : key,
                "type" : value.type.value,
            }
        return json.dumps(data, indent=2)

    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui"]) as queueUI:
            with gr.Column(scale=15):
                radioChoices = [x for x in self._entries.keys()] + [-1]
                if self._selected not in radioChoices:
                    self._selected = -1
                self.radio = gr.Radio(
                    show_label=False,
                    choices=radioChoices,
                    value=self._selected)
                gr.Textbox(interactive=False, value=self._getQueueUIJson())
            with gr.Column(scale=15):
                pause = gr.Button(value=self._getPauseButtonLabel())
                pause.click(
                    fn=self._onTogglePause,
                    outputs=[pause],
                )
                if self._selected == -1:
                    gr.Markdown("Nothing is selected")
                    return
                entry = self._entries[self._selected]
                workflowUI = WorkflowUI(
                            workflow=entry.processing.workflow,
                            name=f'queued {self._selected}',
                            needResizableRow=False)
                workflowUI.runButton.visible = False
                for inputElementUI, inputElementProcessing in zip(
                    workflowUI.inputElements, entry.processing.inputElements
                ):
                    inputElementUI.gradioComponent.interactive = False
                    inputElementUI.gradioComponent.value = inputElementProcessing.value
                # if entry.type == QueueUIEntryType.COMPLETE:


