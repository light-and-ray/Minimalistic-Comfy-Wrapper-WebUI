from mcww.processing import Processing
from mcww.workflow import Workflow, Element
from mcww.comfyAPI import ComfyUIException
import gradio as gr
import time, threading, traceback, uuid


class _Queue:
    def __init__(self):
        self._processingById: dict(int, Processing) = dict()
        self._queueListIds: list[int] = []
        self._completeListIds: list[int] = []
        self._errorListIds: list[int] = []
        self._inProgressId: int|None = None
        self._paused: bool = False
        self._thread = threading.Thread(target=self._queueProcessingLoop, daemon=True)
        self._thread.start()
        self._maxId = 1
        self._pullOutputsIds = dict[str, list[int]]()
        self._queueVersion = 1


    def getOnRunButtonClicked(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element],
            pullOutputsKey: str):
        def onRunButtonClicked(*args):
            processing = Processing(workflow, inputElements, outputElements, self._maxId)
            self._maxId += 1
            processing.initWithArgs(*args)
            self._processingById[processing.id] = processing
            self._queueListIds = [processing.id] + self._queueListIds
            if self._inProgressId or self._paused:
                if self._paused:
                    gr.Info("Queued, paused", 1)
                else:
                    gr.Info("Queued", 1)
            else:
                gr.Info("Started", 1)
            if pullOutputsKey not in self._pullOutputsIds:
                self._pullOutputsIds[pullOutputsKey] = []
            self._pullOutputsIds[pullOutputsKey] = [processing.id] + self._pullOutputsIds[pullOutputsKey]
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
            if pullOutputsKey not in self._pullOutputsIds:
                return nothing()
            for id in self._pullOutputsIds[pullOutputsKey]:
                if id in self._completeListIds:
                    return self.getProcessing(id).getOutputsForCallback()
            return nothing()
        return onPullOutputs


    def getProcessing(self, id: int) -> Processing:
        return self._processingById[id]


    def _queueProcessingLoop(self):
        while True:
            if not self._paused:
                if not self._inProgressId and self._queueListIds:
                    self._inProgressId = self._queueListIds.pop()
                    try:
                        self.getProcessing(self._inProgressId).process()
                    except Exception as e:
                        silent = False
                        if type(e) in [ComfyUIException]:
                            silent=True
                        elif type(e) == OSError and "No route to host" in str(e):
                            silent=True
                        if not silent:
                            print(traceback.format_exc())
                        print(f"Done with error: {e.__class__.__name__}: {e}")
                        self._errorListIds.append(self._inProgressId)
                        self.getProcessing(self._inProgressId).error = e
                    else:
                        print("Done!")
                        self._completeListIds.append(self._inProgressId)
                    self._inProgressId = None
                    self._queueVersion += 1
            time.sleep(0.05)


    def getInProgress(self):
        if self._inProgressId:
            return self.getProcessing(self._inProgressId)

    def getQueueList(self):
        return [self.getProcessing(id) for id in self._queueListIds]

    def getCompleteList(self):
        return [self.getProcessing(id) for id in self._completeListIds]

    def getErrorList(self):
        return [self.getProcessing(id) for id in self._errorListIds]

    def togglePause(self):
        self._paused = not self._paused

    def isPaused(self):
        return self._paused

    def getQueueVersion(self):
        return self._queueVersion

    def getOnPullQueueUpdates(self, oldVersion):
        def onPullQueueUpdates():
            if self.getQueueVersion() > oldVersion:
                return str(uuid.uuid4())
            else:
                return gr.Textbox()
        return onPullQueueUpdates


queue = _Queue()
