from dataclasses import dataclass
from typing import Any
from workflow import Workflow, Element
from nodeUtils import injectValueToNode
from comfy import processComfy
from utils import raiseGradioError
from PIL import Image


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
            node = comfyWorkflow[inputElement.element.index]
            injectValueToNode(node, inputElement.value)
        try:
            nodeToResults = processComfy(comfyWorkflow)
        except Exception as e:
            raiseGradioError(e)
        for nodeIndex, results in nodeToResults.items():
            for outputElement in self._outputElements:
                if str(outputElement.element.index) == str(nodeIndex):
                    outputElement.value = results
        

    def onRunButtonClick(self, *args):
        for i in range(len(args)):
            self._inputElements[i].value = args[i]
        self._process()
        result = []
        for outputElement in self._outputElements:
            if isinstance(outputElement.value, list) and isinstance(outputElement.value[0], Image.Image):
                result.append(x for x in outputElement.value)
        print(result)
        if len(result) == 1:
            return result[0]
        else:
            return result
