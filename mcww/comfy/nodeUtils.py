import json
from typing import Any
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
from mcww.comfy.comfyFile import ComfyFile, getUploadedComfyFile
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
        elif isinstance(value, ComfyFile):
            fileName = value.filename
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
        elif isinstance(value, ComfyFile):
            fileName = value.filename
            node["inputs"]["file"] = fileName
            return
        elif value is None:
            node["inputs"]["file"] = None
            nullifyLinks(workflow, nodeIndex)
            return

    print(value)
    print(json.dumps(node, indent=4))
    raise Exception("Unknown node type")

