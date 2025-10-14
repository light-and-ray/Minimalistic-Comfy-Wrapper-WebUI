from mcww.processing import Processing
from mcww.workflow import Workflow, Element
from mcww.comfyAPI import ComfyUIException
import gradio as gr
import time, threading, traceback


class _Queue:
    def __init__(self):
        self._queueList: list[Processing] = []
        self._completeList: list[Processing] = []
        self._errorList: list[Processing] = []
        self._inProgress: Processing|None = None
        self._paused: bool = True
        self._thread = threading.Thread(target=self._queueProcessingLoop, daemon=True)
        self._thread.start()
        self._maxId = 0

    def getOnRunButtonClicked(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element]):
        def onRunButtonClicked(*args):
            processing = Processing(workflow, inputElements, outputElements, self._maxId)
            self._maxId += 1
            processing.initWithArgs(*args)
            self._queueList.append(processing)
            gr.Info("Queued")
        return onRunButtonClicked

    def _queueProcessingLoop(self):
        while True:
            if not self._paused:
                if not self._inProgress and self._queueList:
                    self._inProgress = self._queueList.pop(0)
                    try:
                        self._inProgress.process()
                    except Exception as e:
                        silent = False
                        if type(e) in [ComfyUIException]:
                            silent=True
                        elif type(e) == OSError and "No route to host" in str(e):
                            silent=True
                        if not silent:
                            print(traceback.format_exc())
                        print(f"Done with error: {e.__class__.__name__}: {e}")
                        self._errorList.append(self._inProgress)
                    else:
                        print("Done!", self._inProgress.getOutputs())
                        self._completeList.append(self._inProgress)
                    self._inProgress = None
            time.sleep(0.05)

    def getInProgress(self):
        return self._inProgress

    def getQueueList(self):
        return self._queueList

    def getCompleteList(self):
        return self._completeList

    def getErrorList(self):
        return self._errorList

    def togglePause(self):
        self._paused = not self._paused

    def isPaused(self):
        return self._paused


queue = _Queue()
