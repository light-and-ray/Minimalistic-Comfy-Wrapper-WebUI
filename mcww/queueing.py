import gradio as gr
import traceback, os, pickle
from datetime import datetime
import urllib.parse
from ffmpy import FFmpeg, FFExecutableNotFoundError
from mcww import opts
from mcww.processing import Processing, ProcessingStatus
from mcww.ui.workflowUI import ElementUI
from mcww.utils import ( saveLogError, getQueueRestoreKey, read_binary_from_file,
    save_binary_to_file, moveValueUp, moveValueDown, zip_cycle,
)
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.comfyAPI import ComfyUIException, ComfyIsNotAvailable, ComfyUIInterrupted

g_thumbnails_supported = True

class _Queue:
    def __init__(self):
        self.restoreKey = getQueueRestoreKey()
        self._processingById: dict(int, Processing) = dict()
        self._allProcessingIds: list[int] = []
        self._paused: bool = False
        self._maxId = 1
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
            print("*** more than 1 IN_PROGRESS processings in the queue")
            return found[0]
        elif len(found) == 0:
            return None
        else:
            return found[0]

    def getInProgressProcessing(self):
        id = self._inProgressId()
        if id:
            return self.getProcessing(id)
        else:
            return None

    @staticmethod
    def _gradioGalleryToPayload(obj):
        if 'image' in obj:
            return obj['image']
        if 'video' in obj:
            return obj['video']
        raise Exception("Can't convert gradio gallery to payload")

    def getOnRunButtonClicked(self, workflow: Workflow, workflowName: str, inputElements: list[Element], outputElements: list[Element],
                mediaSingleElements: list[Element], mediaBatchElements: list[Element], pullOutputsKey: str):
        def onRunButtonClicked(*args):
            try:
                processing = Processing(
                    workflow=workflow,
                    inputElements=inputElements,
                    outputElements=outputElements,
                    mediaElements=mediaSingleElements,
                    id=self._maxId,
                    pullOutputsKey=pullOutputsKey,
                )
                processing.otherDisplayText = workflowName
                self._maxId += 1
                args = list(args)

                indexA = 0
                indexB = len(inputElements)
                inputValues = args[indexA:indexB]
                indexA = indexB
                indexB += len(mediaSingleElements)
                mediaSingleValues = args[indexA:indexB]
                indexA = indexB
                indexB += len(mediaBatchElements)
                mediaBatchValues = args[indexA:indexB]

                selectedMediaTabComponent = args[-1]
                if selectedMediaTabComponent == "tabSingle":
                    mediaBatchValues = [mediaSingleValues]
                elif selectedMediaTabComponent == "tabBatch":
                    mediaBatchValues = list(zip_cycle(*mediaBatchValues))
                    mediaBatchValues = [[self._gradioGalleryToPayload(x) for x in row] for row in mediaBatchValues]

                processing.initValues(
                    inputValues=inputValues,
                    mediaBatchValues=mediaBatchValues,
                )
                self._processingById[processing.id] = processing
                self._allProcessingIds = [processing.id] + self._allProcessingIds
                if self._inProgressId() or self._paused:
                    if self._paused:
                        gr.Info("Queued, paused", 1)
                    else:
                        gr.Info("Queued", 1)
                else:
                    gr.Info("Started", 1)
                self._queueVersion += 1
            except Exception as e:
                text = "Unexpected exception on run button clicked. It's a critical error, please report it on github"
                saveLogError(e, text)
                raise gr.Error(text, print_exception=False)
        return onRunButtonClicked


    def getOnPullOutputs(self, pullOutputsKey: str, outputElementsUI: list[ElementUI]):
        def onPullOutputs():
            inQueueNumber = 0
            batchDone = 0
            batchSize = 1
            isRunning = False
            errorText = ""

            def infoUpdates():
                runningHtmlText = '<div>'
                runningVisible = False
                if isRunning:
                    runningHtmlText += 'Running<span class="running-dots"></span> '
                    runningVisible = True
                    if batchSize > 1:
                        runningHtmlText += f"(batch: {batchDone+1}/{batchSize}) "
                if inQueueNumber:
                    runningHtmlText += f'({inQueueNumber} waiting in queue)'
                    runningVisible = True
                runningHtmlText += '</div>'
                return [gr.HTML(value=runningHtmlText, visible=runningVisible),
                        gr.Markdown(value=errorText, visible=bool(errorText))]

            def nothing():
                return [x.gradioComponent.__class__() for x in outputElementsUI] + infoUpdates()

            for processing in self.getAllProcessings():
                if processing.pullOutputsKey != pullOutputsKey:
                    continue
                batchDone = processing.batchDone
                batchSize = processing.batchSize()
                if not errorText and processing.status == ProcessingStatus.ERROR and processing.error:
                    errorText = processing.error
                if processing.status == ProcessingStatus.QUEUED:
                    inQueueNumber += 1
                if processing.status == ProcessingStatus.IN_PROGRESS:
                    isRunning = True
                if processing.status == ProcessingStatus.COMPLETE \
                        or (ProcessingStatus.IN_PROGRESS and processing.batchDone > 0):
                    foundResultElementKeys = [x.element.getKey() for x in processing.outputElements]
                    neededElementKeys = [x.element.getKey() for x in outputElementsUI]
                    if foundResultElementKeys != neededElementKeys:
                        return nothing()
                    return processing.getOutputsForCallback() + infoUpdates()
            return nothing()
        return onPullOutputs


    def getOnPullPreviousUsedSeed(self, pullOutputsKey: str, elementKey: str):
        def onPullPreviousUsedSeed() -> None:
            def nothing():
                gr.Warning("Not able to pull previously used seed", 2)
                return gr.update()
            for processing in self.getAllProcessings():
                if processing.pullOutputsKey != pullOutputsKey:
                    continue
                for inputElement in processing.inputElements:
                    if inputElement.element.getKey() == elementKey:
                        seed = inputElement.value
                        if seed != -1:
                            return inputElement.value
            return nothing()
        return onPullPreviousUsedSeed


    def getOutputsVersion(self, outputs_key: str):
        return hash(tuple(f'{x.status}/{x.batchDone}' for x in self.getAllProcessings() if x.pullOutputsKey == outputs_key))


    def getProcessing(self, id: int) -> Processing:
        return self._processingById.get(id, None)


    def _handleProcessingError(self, e: Exception, processing: Processing):
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
                self._handleProcessingError(e, processing)
            self._queueVersion += 1
        elif self._inProgressId():
            processing = self.getProcessing(self._inProgressId())
            try:
                needUpdateVersion = processing.iterateProcessing()
            except Exception as e:
                self._handleProcessingError(e, processing)
            else:
                if needUpdateVersion:
                    self._queueVersion += 1


    def getAllProcessingsIds(self):
        return self._allProcessingIds

    def getAllProcessings(self):
        return [self.getProcessing(x) for x in self.getAllProcessingsIds()]

    def togglePause(self):
        self._paused = not self._paused
        self._queueVersion += 1

    def isPaused(self):
        return self._paused

    def getQueueVersion(self):
        return self._queueVersion

    def getQueueIndicator(self):
        if self._paused:
            return "▶\uFE0E"
        size = len(self._queuedListIds())
        if self._inProgressId():
            size += 1
        if size == 0:
            return None
        return size

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
        if processing.status == ProcessingStatus.IN_PROGRESS:
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


    def cleanThumbnails(self):
        self._thumbnailsForUrl = dict[str, str]()
        thumbnailsDirectory = os.path.join(opts.STORAGE_DIRECTORY, "thumbnails")
        for filename in os.listdir(thumbnailsDirectory):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(thumbnailsDirectory, filename)
                os.remove(file_path)


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
            needRemove = self._allProcessingIds[opts.options.maxQueueSize:]
            if len(needRemove) > 0:
                for id in needRemove:
                    del self._processingById[id]
                self._allProcessingIds = self._allProcessingIds[:opts.options.maxQueueSize]
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
