from enum import Enum
import json, re
from typing import Any
from gradio.data_classes import ImageData
from mcww.comfyAPI import getUploadedComfyFile

class DataType(Enum):
    STRING = "string"
    FLOAT = "float"
    INT = "int"
    IMAGE = "image"
    VIDEO = "video"


def getNodeDataTypeAndValue(node: dict) -> DataType:
    try:
        value = node["inputs"]["value"]
        if isinstance(value, int):
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
    pattern = re.compile(r"<([^:]+):([^/:]+)(?:/([^:]+))?:(\d+)>(.*)")

    match = pattern.match(title)

    if match:
        label, category, tab_name, sort_order, other_text = match.groups()

        return {
            "label": label,
            "category": category,
            "tab_name": tab_name if tab_name else "",
            "sort_order": int(sort_order),
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
    return obj


def injectValueToNode(nodeIndex: int, value: Any, workflow: dict) -> None:
    node = workflow[nodeIndex]

    for field in ("value", "text", "prompt"):
        if field in node["inputs"] and (
                type(value) == type(node["inputs"][field])
                or node["inputs"][field] is None
        ):
            node["inputs"][field] = value
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

    print(json.dumps(node, indent=4))
    raise Exception("Unknown node type")

