from dataclasses import dataclass
from enum import Enum
import gradio as gr
from mcww import queueing
from mcww.processing import Processing

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
        self._entries: list[QueueUIEntry] = []
        self._selected = selected
        self._prepareEntries()
        self._buildQueueUI()

    def _prepareEntries(self):
        for processingList, type in zip([
            queueing.queue.getCompleteList(),
            queueing.queue.getErrorList(),
            queueing.queue.getQueueList()], [
                QueueUIEntryType.COMPLETE,
                QueueUIEntryType.ERROR,
                QueueUIEntryType.QUEUED,
        ]):
            for processing in processingList:
                self._entries.append(QueueUIEntry(
                    processing=processing,
                    type=type,
                ))
        self._entries = sorted(self._entries, key=lambda x: x.processing.id)


    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "queue-ui"]) as queueUI:
            with gr.Column(scale=15):
                radioChoices = [x.processing.id for x in self._entries] + [-1]
                if self._selected not in radioChoices:
                    self._selected = -1
                self.radio = gr.Radio(
                    show_label=False,
                    choices=radioChoices,
                    value=self._selected)
            with gr.Column(scale=15):
                if self._selected == -1:
                    return
                gr.Markdown(f"Rendering {self._selected}")


