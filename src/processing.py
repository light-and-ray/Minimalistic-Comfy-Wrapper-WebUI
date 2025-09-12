from dataclasses import dataclass
from typing import Any
from workflow import Workflow, Element

@dataclass
class ElementProcessing:
    element: Element
    value: Any = None


class Processing:
    def __init__(self, workflow: Workflow, inputElements: list[Element], outputElements: list[Element]):
        self._workflow = workflow
        self._inputElements = [ElementProcessing(element=x) for x in inputElements]
        self._outputElements = [ElementProcessing(element=x) for x in outputElements]
    
    def onRunButtonClick(self, *args):
        for i in range(len(args)):
            self._inputElements[i].value = args[i]
        print(f"Got {self._inputElements}")
