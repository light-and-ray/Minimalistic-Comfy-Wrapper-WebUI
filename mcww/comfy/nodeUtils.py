import json, re
from typing import Any
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
from mcww.comfy.comfyAPI import getUploadedComfyFile
from mcww.utils import DataType, isImageExtension, isVideoExtension


def getNodeDataTypeAndValue(node: dict) -> DataType:
    classType = node["class_type"].lower()
    try:
        value = node["inputs"]["value"]
        if isinstance(value, int):
            if "float" in classType:
                return DataType.FLOAT, float(value)
            else:
                return DataType.INT, value
        if isinstance(value, float):
            return DataType.FLOAT, value
        if isinstance(value, str):
            return DataType.STRING, value
    except KeyError:
        pass

    try:
        value = node["inputs"]["text"]
        return DataType.STRING, value
    except KeyError:
        pass

    try:
        value = node["inputs"]["prompt"]
        return DataType.STRING, value
    except KeyError:
        pass

    try:
        node["inputs"]["image"]
        return DataType.IMAGE, None
    except KeyError:
        pass

    try:
        node["inputs"]["images"]
        return DataType.IMAGE, None
    except KeyError:
        pass

    try:
        node["inputs"]["video"]
        return DataType.VIDEO, None
    except KeyError:
        pass

    try:
        file = node["inputs"]["file"]
        if isVideoExtension(file):
            return DataType.VIDEO, None
        if isImageExtension(file):
            return DataType.IMAGE, None
    except KeyError:
        pass

    print(json.dumps(node, indent=4))
    raise Exception("Unknown node type")


def parseMinMaxStep(other_text: str):
    numbers_as_strings = re.findall(r"[-+]?\d*\.?\d+", other_text)

    if len(numbers_as_strings) not in [2, 3]:
        return None

    try:
        min_val = float(numbers_as_strings[0])
        max_val = float(numbers_as_strings[1])
        step_val = float(numbers_as_strings[2]) if len(numbers_as_strings) == 3 else None
    except (IndexError, ValueError) as e:
        return None

    return (min_val, max_val, step_val)



def parse_title(title: str) -> dict or None:
    """
    Parses a string in the format:
    <Label:category[[/accordionName]/tab]:sortRowNumber[/sortColNumber]> other args

    Returns a dictionary with parsed fields, or None if the format doesn't match.
    """
    # Explanation of the new regex pattern:
    # 1. <([^:]+):                 - Start tag, capture Label (Group 1)
    # 2. ([^/:]+)                  - Capture Category (Group 2)
    # 3. (?:/([^/:]+))?            - Optional non-capturing group for the next segment (tab).
    # 5. :(\d+)                    - Separator ':', capture sortRowNumber (Group 5)
    # 6. (?:/(\d+))?               - Optional non-capturing group for '/sortColNumber'. sortColNumber is captured (Group 6).
    # 7. >(.*)                     - End tag '>', capture other args (Group 7)

    pattern = re.compile(
        r"<([^:]+):"               # Group 1: Label
        r"([^/:]+)"                # Group 2: Category
        r"(?:/([^/:]+))?"          # Group 3: Optional tab_name
        r":(\d+)"                  # Group 5: sortRowNumber
        r"(?:/(\d+))?"             # Group 6: Optional sortColNumber
        r">(.*)"                   # Group 7: other_text
    )

    match = pattern.match(title)

    if match:
        label, category, tab_name, sort_row_number_str, sort_col_number_str, other_text = match.groups()
        if tab_name:
            tab_name.strip()
        # Convert sort numbers
        sort_row_number = int(sort_row_number_str)
        # sortColNumber is optional, so it might be None
        sort_col_number = int(sort_col_number_str) if sort_col_number_str else None

        return {
            "label": label.strip(),
            "category": category.strip(),
            "tab_name": tab_name,
            "sort_row_number": sort_row_number,
            "sort_col_number": sort_col_number,
            "other_text": other_text.strip()
        }
    else:
        return None


def nullifyLinks(workflow: dict, nodeIndex: int) -> None:
    for node in workflow.values():
        for inputKey in node["inputs"]:
            if (isinstance(node["inputs"][inputKey], list)
                    and node["inputs"][inputKey]
                    and node["inputs"][inputKey][0] == str(nodeIndex)
            ):
                node["inputs"][inputKey] = None


def toGradioPayload(obj):
    if isinstance(obj, dict) and "mime_type" in obj and "path" in obj:
        if obj["mime_type"].startswith("image"):
            return ImageData.from_json(obj)
    if isinstance(obj, dict) and "video" in obj and "path" in obj["video"]:
        return VideoData.from_json(obj)
    return obj


def injectValueToNode(nodeIndex: int, value: Any, workflow: dict) -> None:
    node = workflow[nodeIndex]
    classType = node["class_type"].lower()

    for field in ("text", "prompt"):
        if field in node["inputs"] and isinstance(value, str):
            node["inputs"][field] = value
            return
    if "value" in node["inputs"]:
        node["inputs"]["value"] = value
        return

    if "image" in node["inputs"]:
        if isinstance(value, ImageData):
            if value.path:
                fileName = getUploadedComfyFile(value.path).filename
            else:
                fileName = value.orig_name
            node["inputs"]["image"] = fileName
            return
        elif value is None:
            node["inputs"]["image"] = None
            nullifyLinks(workflow, nodeIndex)
            return
    if "file" in node["inputs"]:
        if isinstance(value, VideoData):
            if value.video.path:
                fileName = getUploadedComfyFile(value.video.path).filename
                node["inputs"]["file"] = fileName
                return
        elif value is None:
            node["inputs"]["file"] = None
            nullifyLinks(workflow, nodeIndex)
            return

    print(value)
    print(json.dumps(node, indent=4))
    raise Exception("Unknown node type")


if __name__ == "__main__":
    print(parse_title("<Test:cat/tab:10/20> rest"))
    print(parse_title("<Test:cat/tab:10> rest"))
    print(parse_title("<Test:cat:10> rest"))
