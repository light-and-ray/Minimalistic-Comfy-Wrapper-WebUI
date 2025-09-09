from dataclasses import dataclass
import json, copy
from parse_title import parse_title
from workflow_converter import graphToApi

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
            self._originalWorkflow = graphToApi(self._originalWorkflow)
        self._elements: list[Element] = []
        for index, node in self._originalWorkflow.items():
            title: str = node["_meta"]["title"].strip()
            parsed = parse_title(title)
            if not parsed:
                continue
            element = Element(index=index, **parsed)
            if element.category not in ALLOWED_CATEGORIES:
                raise Exception(f'Unknown category in the workflow: "{element.category}". Check the instruction')
            if not element.tab_name:
                element.tab_name = "Other"
            self._elements.append(element)

    def getTabs(self, category: str) -> list[str]:
        sort_orders: dict[str, int] = dict()
        for element in self._elements:
            if element.category != category:
                continue
            existing_sort_order = sort_orders.get(element.tab_name)
            if existing_sort_order is None or existing_sort_order > element.sort_order:
                sort_orders[element.tab_name] = element.sort_order

        return sorted(sort_orders.keys(), key=sort_orders.get)

    def getElements(self, category: str, tab: str) -> list[str]:
        elements: list[Element] = []
        for element in self._elements:
            if element.category == category and element.tab_name == tab:
                elements.append(element)
        elements: list[Element] = sorted(elements, key=lambda e: e.sort_order)
        return elements

    def getOriginalWorkflow(self):
        return copy.deepcopy(self._originalWorkflow)


if __name__ == "__main__":
    with open("../workflows/wan2_2_flf2v.json") as f:
        workflowComfy = f.read()
    workflow = Workflow(workflowComfy)
    
    for category in ALLOWED_CATEGORIES:
        print(f"{category}:")
        tabs: list[str] = workflow.getTabs(category)
        for tab in tabs:
            print(f"    {tab}:")
            for element in workflow.getElements(category, tab):
                print(f"        {element}")
