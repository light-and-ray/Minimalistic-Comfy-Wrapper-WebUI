import gradio as gr
import traceback, os, pickle
from datetime import datetime
import urllib.parse
from ffmpy import FFmpeg, FFExecutableNotFoundError
from mcww import opts
from mcww.processing import Processing, ProcessingStatus
from mcww.utils import ( saveLogError, getStorageEncryptionKey, getStorageKey, read_binary_from_file,
    save_binary_to_file, moveValueUp, moveValueDown,
)
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.comfyAPI import ComfyUIException, ComfyIsNotAvailable, ComfyUIInterrupted

g_thumbnails_supported = True

class _Queue:
    def __init__(self):
        self.restoreKey = f'{getStorageEncryptionKey()}/{getStorageKey()}'
        self._processingById: dict(int, Processing) = dict()
        self._allProcessingIds: list[int] = []
        self._paused: bool = False
        self._maxId = 1
        self._outputsIds = dict[str, list[int]]()
        self._queueVersion = 1
        self._thumbnailsForUrl = dict[str, str]()


    def _queuedListIds(self):
        return list(filter(lambda x: self.getProcessing(x).status == ProcessingStatus.QUEUED, self._allProcessingIds))

    def _completeListIds(self):
        return list(filter(lambda x: self.getProcessing(x).status == ProcessingStatus.COMPLETE, self._allProcessingIds))

    def _errorListIds(self):
        return list(filter(lambda x: self.getProcessing(x).status == ProcessingStatus.ERROR, self._allProcessingIds))

    def _inProgressId(self):
        found = list(filter(lambda x: self.getProcessing(x).status == ProcessingStatus.IN_PROGRESS, self._allProcessingIds))
        if len(found) > 1:
            print("*** more then 1 IN_PROGRESS processings in the queue")
            return found[0]
        elif len(found) == 0:
            return None
        else:
            return found[0]

    def getOnRunButtonClicked(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element],
            pullOutputsKey: str):
        def onRunButtonClicked(*args):
            processing = Processing(workflow, inputElements, outputElements, self._maxId)
            self._maxId += 1
            processing.initWithArgs(*args)
            self._processingById[processing.id] = processing
            self._allProcessingIds = [processing.id] + self._allProcessingIds
            if self._inProgressId() or self._paused:
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
                if id in self._completeListIds():
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
                    if id in self._completeListIds():
                        processing = self.getProcessing(id)
                        for inputElement in processing.inputElements:
                            if inputElement.element.getKey() == elementKey:
                                return inputElement.value
            return nothing()
        return onPullPreviousUsedSeed


    def getOutputsVersion(self, outputs_key: str):
        if outputs_key not in self._outputsIds:
            self._outputsIds[outputs_key] = []
        return hash(tuple(self.getProcessing(x).status for x in self._outputsIds[outputs_key]))


    def getProcessing(self, id: int) -> Processing:
        return self._processingById.get(id, None)


    def _handleProcessingError(self, e: Exception):
        processing = self.getProcessing(id=self._inProgressId())
        silent = False
        if type(e) in [ComfyUIException, ComfyIsNotAvailable, ComfyUIInterrupted]:
            silent=True
        if not silent:
            print(traceback.format_exc())
            saveLogError(e, needPrint=False, prefixTitleLine="Error while processing")
        processing.error = f"Error: {e.__class__.__name__}: {e}"
        processing.status = ProcessingStatus.ERROR
        if type(e) in [ComfyIsNotAvailable]:
            self._paused = True
        self._queueVersion += 1


    def iterateQueueProcessingLoop(self):
        if not self._paused and not self._inProgressId() and self._queuedListIds():
            processing = self.getProcessing(self._queuedListIds()[-1])
            try:
                processing.startProcessing()
            except Exception as e:
                self._handleProcessingError(e)
            self._queueVersion += 1
        elif self._inProgressId():
            processing = self.getProcessing(self._inProgressId())
            try:
                processing.fillResultsIfPossible()
            except Exception as e:
                self._handleProcessingError(e)
            else:
                if processing.status == ProcessingStatus.COMPLETE:
                    self._queueVersion += 1


    def getAllProcessingsIds(self):
        return self._allProcessingIds

    def getAllProcessings(self):
        return [self.getProcessing(x) for x in self.getAllProcessingsIds()]

    def togglePause(self):
        self._paused = not self._paused

    def isPaused(self):
        return self._paused

    def getQueueVersion(self):
        return self._queueVersion

    def interrupt(self):
        if self._inProgressId():
            self.getProcessing(self._inProgressId()).interrupt()

    def restart(self, id: int):
        if id in self._errorListIds():
            processing = self.getProcessing(id)
            processing.error = ""
            processing.status = ProcessingStatus.QUEUED
            self._queueVersion += 1

    def cancel(self, id: int):
        processing = self.getProcessing(id)
        if self._inProgressId() == processing.id:
            self.interrupt()
        elif processing.status == ProcessingStatus.QUEUED:
            processing.status = ProcessingStatus.ERROR
            processing.error = "Canceled by user"
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
            global g_thumbnails_supported
            g_thumbnails_supported = False
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
        if not g_thumbnails_supported: return None
        self._ensureThumbnailForGradioVideo(url)
        path = self._thumbnailsForUrl.get(url, None)
        if path is None:
            return None
        else:
            return f"/gradio_api/file={path}"


    def moveUp(self, id: int):
        if id in self._allProcessingIds:
            self._allProcessingIds = moveValueUp(self._allProcessingIds, id)
            self._queueVersion += 1


    def moveDown(self, id: int):
        if id in self._allProcessingIds:
            self._allProcessingIds = moveValueDown(self._allProcessingIds, id)
            self._queueVersion += 1


    def cleanup(self):
        try:
            needRemove = self._allProcessingIds[opts.maxQueueSize:]
            if len(needRemove) > 0:
                for id in needRemove:
                    del self._processingById[id]
                    outputKeysToRemove = set()
                    for key, outputIds in self._outputsIds.items():
                        if id in outputIds:
                            outputIds.remove(id)
                        if not outputIds:
                            outputKeysToRemove.add(key)
                    for key in outputKeysToRemove:
                        del self._outputsIds[key]
                self._allProcessingIds = self._allProcessingIds[:opts.maxQueueSize]
                # todo: add thumbnails cleaning button
                print(f"Cleaned {len(needRemove)} entries from the queue")
                self._queueVersion += 1
        except Exception as e:
            saveLogError(e, "Error during queue cleanup")


queue: _Queue = None

AUTOSAVE_INTERVAL = 15

def initQueue():
    global queue
    queue = _Queue()
    queueFile = os.path.join(opts.STORAGE_DIRECTORY, "queue.bin")
    restoredQueue = None
    try:
        if os.path.exists(queueFile):
            restoredQueue = pickle.loads(read_binary_from_file(queueFile))
    except Exception as e:
        saveLogError(e, "Exception on queue file loading")
    if restoredQueue and queue.restoreKey == getattr(restoredQueue, 'restoreKey', None):
        queue = restoredQueue


def saveQueue():
    global queue
    queue.cleanup()
    queueFile = os.path.join(opts.STORAGE_DIRECTORY, "queue.bin")
    save_binary_to_file(pickle.dumps(queue), queueFile)
