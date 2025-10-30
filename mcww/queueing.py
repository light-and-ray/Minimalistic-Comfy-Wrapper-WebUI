import gradio as gr
import time, threading, traceback
from mcww.processing import Processing, ProcessingType
from mcww.utils import saveLogError
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.comfyAPI import ComfyUIException, ComfyIsNotAvailable


class _Queue:
    def __init__(self):
        self._processingById: dict(int, Processing) = dict()
        self._queuedListIds: list[int] = []
        self._completeListIds: list[int] = []
        self._errorListIds: list[int] = []
        self._inProgressId: int|None = None
        self._paused: bool = False
        self._thread = threading.Thread(target=self._queueProcessingLoop, daemon=True)
        self._thread.start()
        self._maxId = 1
        self._outputsIds = dict[str, list[int]]()
        self._queueVersion = 1


    def getOnRunButtonClicked(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element],
            pullOutputsKey: str):
        def onRunButtonClicked(*args):
            processing = Processing(workflow, inputElements, outputElements, self._maxId)
            self._maxId += 1
            processing.initWithArgs(*args)
            self._processingById[processing.id] = processing
            self._queuedListIds = [processing.id] + self._queuedListIds
            if self._inProgressId or self._paused:
                if self._paused:
                    gr.Info("Queued, paused", 1)
                else:
                    gr.Info("Queued", 1)
            else:
                gr.Info("Started", 1)
            if pullOutputsKey not in self._outputsIds:
                self._outputsIds[pullOutputsKey] = []
            self._outputsIds[pullOutputsKey] = [processing.id] + self._outputsIds[pullOutputsKey]
            self._queueVersion += 1
        return onRunButtonClicked


    def getOnPullOutputs(self, pullOutputsKey: str, outputComponents: list[gr.Component]):
        def onPullOutputs():
            def nothing():
                result = [x.__class__() for x in outputComponents]
                if len(result) == 1:
                    return result[0]
                else:
                    return result
            if pullOutputsKey not in self._outputsIds:
                return nothing()
            for id in self._outputsIds[pullOutputsKey]:
                if id in self._completeListIds:
                    return self.getProcessing(id).getOutputsForCallback()
            return nothing()
        return onPullOutputs


    def getOnPullPreviousUsedSeed(self, pullOutputsKey: str, elementKey: str):
        def onPullPreviousUsedSeed() -> None:
            def nothing():
                gr.Info("Not able to pull previously used seed", 2)
                return -1
            if pullOutputsKey in self._outputsIds:
                for id in self._outputsIds[pullOutputsKey]:
                    if id in self._completeListIds:
                        processing = self.getProcessing(id)
                        for inputElement in processing.inputElements:
                            if inputElement.element.getKey() == elementKey:
                                return inputElement.value
            return nothing()
        return onPullPreviousUsedSeed


    def getOutputsVersion(self, outputs_key: str):
        if outputs_key not in self._outputsIds:
            self._outputsIds[outputs_key] = []
        return hash(tuple(self.getProcessing(x).type for x in self._outputsIds[outputs_key]))


    def getProcessing(self, id: int) -> Processing:
        return self._processingById[id]


    def _queueProcessingLoop(self):
        while True:
            if not self._paused:
                if not self._inProgressId and self._queuedListIds:
                    self._inProgressId = self._queuedListIds.pop()
                    try:
                        self.getProcessing(self._inProgressId).process()
                    except Exception as e:
                        silent = False
                        if type(e) in [ComfyUIException, ComfyIsNotAvailable]:
                            silent=True
                        if not silent:
                            print(traceback.format_exc())
                            saveLogError(e, needPrint=False, prefixTitleLine="Error while processing")
                        self._errorListIds.append(self._inProgressId)
                        self.getProcessing(self._inProgressId).error = f"Error: {e.__class__.__name__}: {e}"
                        self.getProcessing(self._inProgressId).type = ProcessingType.ERROR
                    else:
                        self._completeListIds.append(self._inProgressId)
                    self._inProgressId = None
                    self._queueVersion += 1
            time.sleep(0.05)

    def getAllProcessingsIds(self):
        ids: list[int] = self._queuedListIds + self._completeListIds + self._errorListIds
        if self._inProgressId:
            ids += [self._inProgressId]
        return ids

    def getAllProcessings(self):
        return [self.getProcessing(x) for x in self.getAllProcessingsIds()]

    def togglePause(self):
        self._paused = not self._paused

    def isPaused(self):
        return self._paused

    def getQueueVersion(self):
        return self._queueVersion


queue = _Queue()
