from dataclasses import dataclass
import json
from parse_title import parse_title

ALLOWED_CATEGORIES: list[str] = ["text_prompt", "image_prompt", "advanced_option",
                "important_option", "output"]


@dataclass
class Element:
    index: str = None
    category: str = None
    tab_name: str = None
    label: str = None
    sort_order: int = None
    other_text: str = None


class Workflow:
    def __init__(self, workflowComfy: str):
        self.setWorkflow(workflowComfy)
    
    def setWorkflow(self, workflowComfy: str):
        self._originalWorkflow: dict = json.loads(workflowComfy)
        if "nodes" in self._originalWorkflow:
            raise Exception("The workflow is not in API format")
        self.elements: list[Element] = []
        for index, node in self._originalWorkflow.items():
            title: str = node["_meta"]["title"].strip()
            parsed = parse_title(title)
            if not parsed:
                continue
            element = Element(index=index, **parsed)
            self.elements.append(element)


if __name__ == "__main__":
    with open("../workflows/test.json") as f:
        workflowComfy = f.read()
    workflow = Workflow(workflowComfy)
    for element in workflow.elements:
        print(element)
