from dataclasses import dataclass
from enum import Enum
import gradio as gr
from mcww import queueing
from mcww.processing import Processing
from mcww.workflowUI import WorkflowUI

class QueueUIEntryType(Enum):
    QUEUED = "queued"
    ERROR = "error"
    COMPLETE = "complete"


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
        for processingList, type in zip([
            queueing.queue.getCompleteList(),
            queueing.queue.getErrorList(),
            queueing.queue.getQueueList()], [
                QueueUIEntryType.COMPLETE,
                QueueUIEntryType.ERROR,
                QueueUIEntryType.QUEUED,
        ]):
            for processing in processingList:
                values.append(QueueUIEntry(
                    processing=processing,
                    type=type,
                ))
        for value in values:
            self._entries[value.processing.id] = value
        sortedKeys = sorted(self._entries.keys())
        self._entries = {key: self._entries[key] for key in sortedKeys}


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
            with gr.Column(scale=15):
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



