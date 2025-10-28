from dataclasses import dataclass
import json, copy
from collections import defaultdict
from mcww.comfy.workflowConverting import graphToApi
from mcww.comfy.nodeUtils import parse_title

ALLOWED_CATEGORIES: list[str] = ["prompt", "advanced", "important", "output"]


@dataclass
class Element:
    index: str = None
    category: str = None
    tab_name: str = None
    label: str = None
    sort_row_number: int = None
    sort_col_number: int = None
    other_text: str = None
    def getKey(self):
        return f"{self.index}/{self.category}/{self.label}/{self.other_text}/{self.tab_name}"
    def isSeed(self):
        return "seed" in self.label.lower() and not self.other_text


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
            if element.category in ALLOWED_CATEGORIES:
                element.category = element.category.lower().removesuffix('s')
            if not element.tab_name:
                element.tab_name = "Other"
            self._elements.append(element)


    def getTabs(self, category: str) -> list[str]:
        sort_orders: dict[str, int] = dict()
        for element in self._elements:
            if element.category != category:
                continue
            existing_sort_order = sort_orders.get(element.tab_name)
            if existing_sort_order is None or existing_sort_order > element.sort_row_number:
                sort_orders[element.tab_name] = element.sort_row_number

        return sorted(sort_orders.keys(), key=sort_orders.get)


    def getElements(self, category: str, tab: str) -> list[list['Element']]:
        # 1. Filter elements by category and tab
        filtered_elements: list['Element'] = []
        for element in self._elements:
            if element.category == category and element.tab_name == tab:
                filtered_elements.append(element)

        # 2. Group elements by row number and handle sort_col_number being None
        # We need a way to distinguish between elements with sort_col_number=None
        # and those with sort_col_number != None but sharing the same sort_row_number.

        # Elements with sort_col_number != None are grouped by row number.
        # Key: sort_row_number
        grouped_by_row: dict[int, list['Element']] = defaultdict(list)

        # Elements with sort_col_number == None are treated as a single-element 'row' each.
        # Key: sort_row_number, Value: list of single-element lists
        single_element_rows: dict[int, list[list['Element']]] = defaultdict(list)

        for element in filtered_elements:
            if element.sort_col_number is None:
                # Treat elements with None column number as a separate row of size 1
                # Note: We still group them by sort_row_number for correct overall row sorting later.
                single_element_rows[element.sort_row_number].append([element])
            else:
                # Elements with a column number are grouped together by row number
                grouped_by_row[element.sort_row_number].append(element)

        # 3. Sort elements within each 'multi-column' row by column number
        # and combine all row-lists into a master dictionary keyed by row number.

        # This dictionary will hold all lists of Elements, keyed by their row number.
        # Value will be a list of lists of Elements (since single-element rows are already lists of lists)
        rows_by_number: dict[int, list[list['Element']]] = defaultdict(list)

        # a. Process multi-column rows
        for row_number, elements_list in grouped_by_row.items():
            if elements_list: # Should always be true, but good practice
                # Sort the list of elements by their 'sort_col_number'
                # We can safely assume sort_col_number is not None here
                sorted_elements_list: list['Element'] = sorted(elements_list, key=lambda e: e.sort_col_number)
                # This sorted list of elements is a single 'row' (list of elements)
                rows_by_number[row_number].append(sorted_elements_list)

        # b. Process single-element rows (which are already lists of lists)
        # Note: The existing logic in single_element_rows already has the form {row_num: [[e1], [e2], ...]}
        for row_number, single_rows_list in single_element_rows.items():
            # Extend the list of lists for this row number
            rows_by_number[row_number].extend(single_rows_list)

        # 4. Sort the rows themselves by row number and flatten the list of lists of lists

        # a. Sort the dictionary items by row number (the key)
        sorted_rows_list_of_tuples: list[tuple[int, list[list['Element']]]] = sorted(
            rows_by_number.items(),
            key=lambda item: item[0]  # Sort by the key (row number)
        )

        # b. Extract and flatten: take the list of lists of Elements and flatten it
        result_list_of_lists: list[list['Element']] = []
        for _, list_of_lists_of_elements in sorted_rows_list_of_tuples:
            # list_of_lists_of_elements contains:
            # - [the_sorted_multi_col_row] (if it exists)
            # - [the_single_element_row_1], [the_single_element_row_2], ... (if they exist)
            result_list_of_lists.extend(list_of_lists_of_elements)

        return result_list_of_lists


    def getOriginalWorkflow(self):
        return copy.deepcopy(self._originalWorkflow)

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


if __name__ == "__main__":
    from utils import read_string_from_file
    workflowComfy = read_string_from_file("../workflows/wan2_2_flf2v.json")
    workflow = Workflow(workflowComfy)

    for category in ALLOWED_CATEGORIES:
        print(f"{category}:")
        tabs: list[str] = workflow.getTabs(category)
        for tab in tabs:
            print(f"    {tab}:")
            for element in workflow.getElements(category, tab):
                print(f"        {element}")
