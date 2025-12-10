from dataclasses import dataclass
import copy, json
from collections import defaultdict
from mcww.utils import DataType
from mcww.comfy.comfyFile import ComfyFile
from mcww.comfy.workflowConverting import graphToApi, WorkflowIsNotSupported
from mcww.comfy.comfyUtils import parse_title, parseMinMaxStep
from mcww.comfy.nodeUtils import getElementField, Field, removeInactiveNodes

ALLOWED_CATEGORIES: list[str] = ["prompt", "advanced", "important", "output"]


@dataclass
class Element:
    nodeIndex: int = None
    category: str = None
    tab_name: str = None
    label: str = None
    sort_row_number: int = None
    sort_col_number: int = None
    other_text: str = None
    field: Field = None
    def getKey(self):
        key = f"{self.nodeIndex}/{self.category}/{self.label}/{self.other_text}/{self.tab_name}/"
        key += f"{self.field.type}/{self.field.name}/"
        if isinstance(self.field.defaultValue, ComfyFile):
            key += f"{self.field.defaultValue.filename}/{self.field.defaultValue.subfolder}"
        else:
            key += f"{self.field.defaultValue}"
        return key
    def isSeed(self):
        return "seed" in self.label.lower() and not self.other_text and self.field.type == DataType.INT
    def parseMinMaxStep(self):
        return parseMinMaxStep(self.other_text)
    def showDefault(self):
        if self.other_text.lower().strip() == "show_default":
            return True
        return False
    def isJson(self):
        return self.other_text.lower().strip() == "json"


class Workflow:
    def __init__(self, workflowComfy: dict):
        self.setWorkflow(workflowComfy)

    def setWorkflow(self, workflowComfy: dict):
        self._workflowDict: dict = workflowComfy
        if "nodes" in self._workflowDict:
            self._workflowDict = graphToApi(self._workflowDict)
        self._elements: list[Element] = []
        for index, node in self._workflowDict.items():
            title: str = node["_meta"]["title"].strip()
            parsed = parse_title(title)
            if not parsed:
                continue
            element = Element(nodeIndex=index, **parsed)
            insensitiveCategory = element.category.lower().removesuffix('s')
            if insensitiveCategory in ALLOWED_CATEGORIES:
                element.category = insensitiveCategory
            if not element.tab_name:
                element.tab_name = "Other"
            isInput = element.category != "output"
            element.field = getElementField(node, isInput)
            if not element.field or not element.field.type:
                raise WorkflowIsNotSupported(f"unknown element type for node {json.dumps(node, indent=2)}")
            self._elements.append(element)
        removeInactiveNodes(self._workflowDict, [x.nodeIndex for x in self._elements])


    def getTabs(self, category: str) -> list[str]:
        sort_orders: dict[str, int] = dict()
        for element in self._elements:
            if element.category != category:
                continue
            existing_sort_order = sort_orders.get(element.tab_name)
            if existing_sort_order is None or existing_sort_order > element.sort_row_number:
                sort_orders[element.tab_name] = element.sort_row_number

        return sorted(sort_orders.keys(), key=sort_orders.get)


    def getElementsRows(self, category: str, tab: str) -> list[list['Element']]:
        filtered_elements: list['Element'] = []
        for element in self._elements:
            if element.category == category and element.tab_name == tab:
                filtered_elements.append(element)

        multiElementsRows: dict[int, list['Element']] = defaultdict(list)
        singleElementListsOfRows: dict[int, list[list['Element']]] = defaultdict(list)
        allListsOfRows: dict[int, list[list['Element']]] = defaultdict(list)

        for element in filtered_elements:
            if element.sort_col_number is not None:
                multiElementsRows[element.sort_row_number].append(element)
            else:
                singleElementListsOfRows[element.sort_row_number].append([element])

        for rowNumber, row in multiElementsRows.items():
            sortedRow: list['Element'] = sorted(row, key=lambda e: e.sort_col_number)
            allListsOfRows[rowNumber].append(sortedRow)

        for rowNumber, listOfRows in singleElementListsOfRows.items():
            allListsOfRows[rowNumber].extend(listOfRows)

        allListsOfRows = {key: allListsOfRows[key] for key in sorted(allListsOfRows.keys())}
        allRows: list[list['Element']] = []
        for listOfRows in allListsOfRows.values():
            allRows.extend(listOfRows)
        return allRows


    def getWorkflowDictCopy(self):
        return copy.deepcopy(self._workflowDict)

    def categoryExists(self, category: str):
        return any([element.category == category for element in self._elements])

    def isValid(self):
        if not any([element.category in ("output") for element in self._elements]):
            return False
        if not any([element.category in ("prompt") for element in self._elements]):
            return False
        return True

    def getCustomCategories(self):
        categories = set([element.category for element in self._elements])
        return [category for category in categories if category not in ALLOWED_CATEGORIES]


    def getTotalActiveNodes(self):
        outputNodesIndexes = [x.nodeIndex for x in self._elements if x.category == "output"]
        workflowDictCopy = self.getWorkflowDictCopy()
        removeInactiveNodes(workflowDictCopy, outputNodesIndexes)
        return len(workflowDictCopy)


if __name__ == "__main__":
    from utils import read_string_from_file
    workflowComfy = read_string_from_file("../workflows/wan2_2_flf2v.json")
    workflow = Workflow(workflowComfy)

    for category in ALLOWED_CATEGORIES:
        print(f"{category}:")
        tabs: list[str] = workflow.getTabs(category)
        for tab in tabs:
            print(f"    {tab}:")
            for element in workflow.getElementsRows(category, tab):
                print(f"        {element}")
