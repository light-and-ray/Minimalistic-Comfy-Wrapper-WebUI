from dataclasses import dataclass
from enum import Enum
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
    value: list[ComfyFile] = None


class ProcessingStatus(Enum):
    QUEUED = "queued"
    ERROR = "error"
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element],
                id: int, pullOutputsKey: str):
        self.workflow = workflow
        self.otherDisplayText = ""
        self.inputElements = [ElementProcessing(element=x) for x in inputElements]
        self.outputElements = [ElementProcessing(element=x) for x in outputElements]
        self.error: str|None = None
        self.id: int = id
        self.prompt_id: str|None = None
        self.status: ProcessingStatus = ProcessingStatus.QUEUED
        self.needUnQueueFlag: bool = False
        self.totalActiveNodes: int = self.workflow.getTotalActiveNodes()
        self.totalCachedNodes = 0
        self.pullOutputsKey = pullOutputsKey


    def startProcessing(self):
        self._uploadAllInputFiles()
        comfyWorkflow = self.workflow.getWorkflowDictCopy()
        for inputElement in self.inputElements:
            if inputElement.element.isSeed() and inputElement.value == -1:
                inputElement.value = generateSeed()
            injectValueToNode(inputElement.element.nodeIndex, inputElement.element.field, inputElement.value, comfyWorkflow)
        self.status = ProcessingStatus.IN_PROGRESS
        self.prompt_id = str(uuid.uuid4())
        enqueueComfy(comfyWorkflow, self.prompt_id)


    def fillResultsIfPossible(self):
        if self.needUnQueueFlag:
            self.needUnQueueFlag = False
            raise ComfyUIInterrupted("Unqueued")
        comfyWorkflow = self.workflow.getWorkflowDictCopy()
        nodeToResults: dict | None = getResultsIfPossible(comfyWorkflow, self.prompt_id)
        if not nodeToResults:
            return None
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self.outputElements:
                if str(outputElement.element.nodeIndex) == str(nodeIndex):
                    outputElement.value = results
        if any(x.value is None for x in self.outputElements):
            saveLogJson(comfyWorkflow, "null_output_workflow")
            raise ComfyUIException("Not all outputs are valid. Check ComfyUI console for details, "
                "or null_output_workflow in logs")
        self.status = ProcessingStatus.COMPLETE


    def interrupt(self):
        if self.status == ProcessingStatus.IN_PROGRESS:
            unQueueComfy(self.prompt_id)
            interruptComfy(self.prompt_id)
            self.needUnQueueFlag = True


    def initWithArgs(self, *args):
        for i in range(len(args)):
            obj = args[i]
            obj = toGradioPayload(obj)
            self.inputElements[i].value = obj
        self._uploadAllInputFiles()


    def _uploadAllInputFiles(self):
        try:
            for inputElement in self.inputElements:
                if isinstance(inputElement.value, ImageData):
                    if inputElement.value.path:
                        inputElement.value = getUploadedComfyFile(inputElement.value.path)
                elif isinstance(inputElement.value, VideoData):
                    if inputElement.value.video.path:
                        inputElement.value = getUploadedComfyFile(inputElement.value.video.path)
                elif isinstance(inputElement.value, FileData):
                    if isAudioExtension(inputElement.value.path):
                        inputElement.value = getUploadedComfyFile(inputElement.value.path)
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

