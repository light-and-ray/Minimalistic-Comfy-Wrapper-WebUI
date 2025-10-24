from dataclasses import dataclass
import gradio as gr
from gradio.components.video import VideoData
from mcww import queueing
from mcww.comfyAPI import ComfyFile, ImageData
from mcww.processing import Processing, ProcessingType
from mcww.workflowUI import WorkflowUI
from mcww.utils import getMcwwLoaderHTML, getRunJSFunctionKwargs, saveLogError, showRenderingErrorGradio
import json, uuid


class QueueUI:
    def __init__(self, mainUIPageRadio: gr.Radio, webui: gr.Blocks):
        self._entries: dict[int, Processing] = dict()
        self._entries_last_version: int = -1
        self.mainUIPageRadio = mainUIPageRadio
        self.webui = webui
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
            fileUrl: str|None = None
            for outputElement in value.outputElements:
                if isinstance(outputElement.value, list):
                    for listEntry in outputElement.value:
                        if isinstance(listEntry, ComfyFile):
                            fileUrl = listEntry.getUrl()
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
                    try:
                        if mainUIPage != "queue": return

                        pullQueueUpdatesButton = gr.Button(json.dumps({
                                    "type": "queue",
                                    "oldVersion": queueing.queue.getQueueVersion(),
                                }),
                                elem_classes=["mcww-pull", "mcww-hidden"])
                        pullQueueUpdatesButton.click(
                            fn=lambda: (str(uuid.uuid4()), str(uuid.uuid4())),
                            inputs=[],
                            outputs=[self.refreshWorkflowTrigger, self.refreshRadioTrigger],
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
                                        queueMode=True)
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
                        saveLogError(e)
                        showRenderingErrorGradio(e)


