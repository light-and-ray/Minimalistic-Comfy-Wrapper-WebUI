import gradio as gr
import traceback, os
from datetime import datetime
import urllib.parse
from ffmpy import FFmpeg, FFExecutableNotFoundError
from mcww import opts
from mcww.processing import Processing, ProcessingType
from mcww.utils import saveLogError
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.comfyAPI import ComfyUIException, ComfyIsNotAvailable, ComfyUIInterrupted


class _Queue:
    def __init__(self):
        self._processingById: dict(int, Processing) = dict()
        self._queuedListIds: list[int] = []
        self._completeListIds: list[int] = []
        self._errorListIds: list[int] = []
        self._inProgressId: int|None = None
        self._paused: bool = False
        self._maxId = 1
        self._outputsIds = dict[str, list[int]]()
        self._queueVersion = 1
        self._thumbnailsForUrl = dict[str, str]()


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


    def _handleProcessingError(self, e: Exception):
        processing = self.getProcessing(id=self._inProgressId)
        silent = False
        if type(e) in [ComfyUIException, ComfyIsNotAvailable, ComfyUIInterrupted]:
            silent=True
        if not silent:
            print(traceback.format_exc())
            saveLogError(e, needPrint=False, prefixTitleLine="Error while processing")
        self._errorListIds.append(processing.id)
        processing.error = f"Error: {e.__class__.__name__}: {e}"
        processing.type = ProcessingType.ERROR
        self._inProgressId = None
        if type(e) == ComfyUIInterrupted:
            self._paused = True
        self._queueVersion += 1


    def iterateQueueProcessingLoop(self):
        if not self._paused and not self._inProgressId and self._queuedListIds:
            self._inProgressId = self._queuedListIds.pop()
            processing = self.getProcessing(self._inProgressId)
            try:
                processing.startProcessing()
            except Exception as e:
                self._handleProcessingError(e)
            self._queueVersion += 1
        elif self._inProgressId:
            processing = self.getProcessing(self._inProgressId)
            try:
                processing.fillResultsIfPossible()
            except Exception as e:
                self._handleProcessingError(e)
            else:
                if processing.type == ProcessingType.COMPLETE:
                    self._completeListIds.append(self._inProgressId)
                    self._inProgressId = None
                    self._queueVersion += 1


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

    def interrupt(self):
        if self._inProgressId:
            self.getProcessing(self._inProgressId).interrupt()
        else:
            self._paused = True
            self._queueVersion += 1

    def restart(self, id: int):
        if id in self._errorListIds:
            self._errorListIds.remove(id)
            self._queuedListIds.insert(0, id)
            self._queueVersion += 1


    def _generateThumbnail(self, videoPath: str) -> str:
        thumbnailsDirectory = os.path.join(opts.STORAGE_DIRECTORY, "thumbnails")
        os.makedirs(thumbnailsDirectory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        thumbnailPath = os.path.join(thumbnailsDirectory, f"{timestamp}.jpg")
        try:
            ff = FFmpeg(
                global_options=['-hide_banner', '-loglevel', 'error'],
                inputs={videoPath: ['-sseof', '-1']},
                outputs={thumbnailPath: ['-vframes', '1', '-q:v', '2']}
            )
            ff.run()
        except FFExecutableNotFoundError:
            print("*** ffmpeg executable not found for video thumbnail generation, skipping.")
            return None
        except Exception as e:
            saveLogError(e, "An unexpected error on thumbnail generation")
            return None
        return thumbnailPath


    def _ensureThumbnailForGradioVideo(self, url: str):
        if url in self._thumbnailsForUrl:
            return
        if not url.startswith("/gradio_api/file="):
            return
        path = urllib.parse.unquote(url.removeprefix("/gradio_api/file="))
        thumbnailPath = self._generateThumbnail(path)
        self._thumbnailsForUrl[url] = thumbnailPath


    def getThumbnailUrlForVideoUrl(self, url) -> str | None:
        self._ensureThumbnailForGradioVideo(url)
        path = self._thumbnailsForUrl.get(url, None)
        if path is None:
            return None
        else:
            return f"/gradio_api/file={path}"


queue = _Queue()
