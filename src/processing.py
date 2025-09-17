from dataclasses import dataclass
from typing import Any
from workflow import Workflow, Element
from nodeUtils import injectValueToNode
from comfyAPI import processComfy
from utils import raiseGradioError


@dataclass
class ElementProcessing:
    element: Element
    value: Any = None


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element]):
        self._workflow = workflow
        self._inputElements = [ElementProcessing(element=x) for x in inputElements]
        self._outputElements = [ElementProcessing(element=x) for x in outputElements]


    def _process(self):
        comfyWorkflow = self._workflow.getOriginalWorkflow()
        for inputElement in self._inputElements:
            injectValueToNode(inputElement.element.index, inputElement.value, comfyWorkflow)
        nodeToResults = processComfy(comfyWorkflow)
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self._outputElements:
                if str(outputElement.element.index) == str(nodeIndex):
                    outputElement.value = results


    def onRunButtonClick(self, *args):
        try:
            for i in range(len(args)):
                self._inputElements[i].value = args[i]
            self._process()
            result = []
            for outputElement in self._outputElements:
                result.append([x.getGradioGallery() for x in outputElement.value])
            if len(result) == 1:
                return result[0]
            else:
                return result
        except Exception as e:
            raiseGradioError(e)
