from dataclasses import dataclass
from typing import Any
from mcww.workflow import Workflow, Element
from mcww.nodeUtils import injectValueToNode
from mcww.comfyAPI import ComfyUIException, processComfy
from mcww.utils import raiseGradioError


@dataclass
class ElementProcessing:
    element: Element
    value: Any = None


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element], id: int):
        self.workflow = workflow
        self.inputElements = [ElementProcessing(element=x) for x in inputElements]
        self.outputElements = [ElementProcessing(element=x) for x in outputElements]
        self.error: Exception|None = None
        self.id: int = id


    def process(self):
        comfyWorkflow = self.workflow.getOriginalWorkflow()
        for inputElement in self.inputElements:
            injectValueToNode(inputElement.element.index, inputElement.value, comfyWorkflow)
        nodeToResults = processComfy(comfyWorkflow)
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self.outputElements:
                if str(outputElement.element.index) == str(nodeIndex):
                    outputElement.value = results

    def initWithArgs(self, *args):
        for i in range(len(args)):
            self.inputElements[i].value = args[i]


    def getOutputs(self):
        result = []
        for outputElement in self.outputElements:
            result.append([x.getGradioGallery() for x in outputElement.value])
        if len(result) == 1:
            return result[0]
        else:
            return result

