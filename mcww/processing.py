from dataclasses import dataclass
from enum import Enum
from typing import Any
import uuid
from gradio import FileData
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
from mcww.comfy.comfyUtils import ComfyIsNotAvailable
from mcww.utils import DataType, generateSeed, isAudioExtension, saveLogJson
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.nodeUtils import injectValueToNode, toGradioPayload
from mcww.comfy.comfyAPI import ( ComfyUIException, ComfyUIInterrupted, enqueueComfy,
    getResultsIfPossible, unQueueComfy, interruptComfy,
)
from mcww.comfy.comfyFile import ComfyFile, getUploadedComfyFile


@dataclass
class ElementProcessing:
    element: Element
    value: Any|list[ComfyFile] = None


@dataclass
class BatchingElementProcessing:
    element: Element
    batchValues: list[Any|ComfyFile] = None


class ProcessingStatus(Enum):
    QUEUED = "queued"
    ERROR = "error"
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element],
                mediaElements: list[list[Element]], id: int, pullOutputsKey: str):
        self.workflow = workflow
        self.otherDisplayText = ""
        self.inputElements = [ElementProcessing(element=x) for x in inputElements]
        self.outputElements = [ElementProcessing(element=x) for x in outputElements]
        self.mediaElements = [BatchingElementProcessing(element=x) for x in mediaElements]
        self.error: str|None = None
        self.id: int = id
        self.prompt_id: str|None = None
        self.status: ProcessingStatus = ProcessingStatus.QUEUED
        self.needUnQueueFlag: bool = False
        self.totalActiveNodes: int = self.workflow.getTotalActiveNodes()
        self.totalCachedNodes = 0
        self.pullOutputsKey = pullOutputsKey
        self.batchDone: int = 0


    def batchSize(self):
        if len(self.mediaElements) == 0:
            return 1
        return len(self.mediaElements[0].batchValues)


    def _startProcessingBatch(self, batchIndex):
        comfyWorkflow = self.workflow.getWorkflowDictCopy()
        def inject(element: Element, value):
            injectValueToNode(element.nodeIndex, element.field, value, comfyWorkflow)

        for inputElement in self.inputElements:
            if inputElement.element.isSeed() and inputElement.value == -1:
                inputElement.value = generateSeed()
            inject(inputElement.element, inputElement.value)

        for mediaElement in self.mediaElements:
            inject(mediaElement.element, mediaElement.batchValues[batchIndex])

        self.prompt_id = str(uuid.uuid4())
        enqueueComfy(comfyWorkflow, self.prompt_id)


    def startProcessing(self):
        self._uploadAllInputFiles()
        self._startProcessingBatch(self.batchDone)
        self.status = ProcessingStatus.IN_PROGRESS


    def iterateProcessing(self):
        if self.needUnQueueFlag:
            self.needUnQueueFlag = False
            raise ComfyUIInterrupted("Unqueued")
        nodeToResults: dict | None = getResultsIfPossible(self.prompt_id)
        if not nodeToResults:
            return False
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self.outputElements:
                if str(outputElement.element.nodeIndex) == str(nodeIndex):
                    if outputElement.value is None:
                        outputElement.value = []
                    outputElement.value.extend(results)
        if any(x.value is None for x in self.outputElements):
            raise ComfyUIException("Not all outputs are valid. Check ComfyUI console for details, "
                "or null_output_workflow in logs")
        self.batchDone += 1
        if self.batchDone >= self.batchSize():
            self.status = ProcessingStatus.COMPLETE
        else:
            self._startProcessingBatch(self.batchDone)
        return True


    def interrupt(self):
        if self.status == ProcessingStatus.IN_PROGRESS:
            unQueueComfy(self.prompt_id)
            interruptComfy(self.prompt_id)
            self.needUnQueueFlag = True


    def initValues(self, inputValues: list, mediaBatchValues: list[list]):
        for i in range(len(inputValues)):
            obj = inputValues[i]
            obj = toGradioPayload(obj)
            self.inputElements[i].value = obj
        for batchIndex in range(len(mediaBatchValues)):
            for i in range(len(mediaBatchValues[batchIndex])):
                obj = mediaBatchValues[batchIndex][i]
                obj = toGradioPayload(obj)
                if self.mediaElements[i].batchValues is None:
                    self.mediaElements[i].batchValues = [None] * len(mediaBatchValues)
                self.mediaElements[i].batchValues[batchIndex] = obj
        self._uploadAllInputFiles()


    def _uploadAllInputFiles(self):
        try:
            def uploadValue(value):
                if isinstance(value, ImageData):
                    if value.path:
                        value = getUploadedComfyFile(value.path)
                elif isinstance(value, VideoData):
                    if value.video.path:
                        value = getUploadedComfyFile(value.video.path)
                elif isinstance(value, FileData):
                    if isAudioExtension(value.path):
                        value = getUploadedComfyFile(value.path)

            for inputElement in self.inputElements:
                uploadValue(inputElement.value)

            for mediaElement in self.mediaElements:
                for value in mediaElement.batchValues:
                    uploadValue(value)

        except ComfyIsNotAvailable:
            pass


    def _getOutputs(self, comfyFileMethod: str):
        result = []
        for outputElement in self.outputElements:
            if outputElement.element.field.type in (DataType.IMAGE, DataType.VIDEO): # gr.Gallery
                result.append([getattr(x, comfyFileMethod)() for x in outputElement.value])
            elif outputElement.element.field.type == DataType.AUDIO: # gr.Audio
                result.append(getattr(outputElement.value[0], comfyFileMethod)())
        return result

    def getOutputsForCallback(self):
        return self._getOutputs("getGradioOutput")

    def getOutputsForComponentInit(self):
        return self._getOutputs("getGradioOutputForComponentInit")

