from dataclasses import dataclass
from mcww.comfy.workflow import Element

@dataclass
class PresetsUIState:
    textPromptElementUiList: list[Element]
    workflowName: str


