from dataclasses import dataclass
from typing import Any
from enum import Enum
import json
from mcww.utils import generateSeed, saveLogJson
from mcww.comfy.workflow import Workflow, Element
from mcww.comfy.nodeUtils import injectValueToNode, toGradioPayload
from mcww.comfy.comfyAPI import ComfyUIException, enqueueComfy, getResultsIfPossible


@dataclass
class ElementProcessing:
    element: Element
    value: Any = None


class ProcessingType(Enum):
    QUEUED = "queued"
    ERROR = "error"
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element], id: int):
        self.workflow = workflow
        self.inputElements = [ElementProcessing(element=x) for x in inputElements]
        self.outputElements = [ElementProcessing(element=x) for x in outputElements]
        self.error: str|None = None
        self.id: int = id
        self.prompt_id: str|None = None
        self.type: ProcessingType = ProcessingType.QUEUED


    def startProcessing(self):
        comfyWorkflow = self.workflow.getOriginalWorkflow()
        for inputElement in self.inputElements:
            if inputElement.element.isSeed() and inputElement.value == -1:
                inputElement.value = generateSeed()
            injectValueToNode(inputElement.element.index, inputElement.value, comfyWorkflow)
        self.prompt_id = enqueueComfy(comfyWorkflow)
        self.type = ProcessingType.IN_PROGRESS


    def fillResultsIfPossible(self):
        comfyWorkflow = self.workflow.getOriginalWorkflow()
        nodeToResults: dict | None = getResultsIfPossible(comfyWorkflow, self.prompt_id)
        if not nodeToResults:
            return None
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self.outputElements:
                if str(outputElement.element.index) == str(nodeIndex):
                    outputElement.value = results
        if any(x.value is None for x in self.outputElements):
            saveLogJson(comfyWorkflow, "null_output_workflow")
            raise ComfyUIException("Not all outputs are valid. Check ComfyUI console for details, "
                "or null_output_workflow in logs")
        self.type = ProcessingType.COMPLETE

    def initWithArgs(self, *args):
        for i in range(len(args)):
            obj = args[i]
            obj = toGradioPayload(obj)
            self.inputElements[i].value = obj


    def getOutputsForCallback(self):
        result = []
        for outputElement in self.outputElements:
            result.append([x.getGradioGallery() for x in outputElement.value])
        if len(result) == 1:
            return result[0]
        else:
            return result


    def getOutputsForComponentInit(self):
        result = []
        for outputElement in self.outputElements:
            result.append([json.loads(x.getGradioGallery().model_dump_json()) for x in outputElement.value])
        return result

