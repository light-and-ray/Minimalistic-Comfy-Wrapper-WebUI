from dataclasses import dataclass
from mcww.utils import DataType
from mcww.comfy.comfyFile import ComfyFile
import json, requests, os
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
from mcww import opts
from mcww.utils import ( DataType, isImageExtension, isVideoExtension,
    read_string_from_file, save_string_to_file, saveLogError,
)
from mcww.comfy.comfyFile import ComfyFile, getUploadedComfyFile
from mcww.comfy.comfyUtils import getHttpComfyPathUrl
from mcww.comfy.comfyAPI import ComfyIsNotAvailable


@dataclass
class Field:
    name: str
    type: DataType
    defaultValue: str


def getNodeDataTypeAndValueLegacy(node: dict):
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


def injectValueToNode(nodeIndex: int, field: Field, value, workflow: dict) -> None:
    if isinstance(value, ImageData):
        if value.path:
            value = getUploadedComfyFile(value.path).filename
        else:
            value = value.orig_name
    elif isinstance(value, VideoData):
        if value.video.path:
            value = getUploadedComfyFile(value.video.path).filename
    elif isinstance(value, ComfyFile):
        value = value.filename

    workflow[nodeIndex]["inputs"][field.name] = value
    if value is None:
        nullifyLinks(workflow, nodeIndex)


_OBJECT_INFO: dict|None = None
def objectInfo():
    _object_info_backup_path = os.path.join(opts.STORAGE_DIRECTORY, "object_info_backup.json")
    global _OBJECT_INFO
    if _OBJECT_INFO is None:
        try:
            url = getHttpComfyPathUrl("/object_info")
            response = requests.get(url)
            response.raise_for_status()
            _OBJECT_INFO = response.json()
            if not _OBJECT_INFO:
                raise Exception("Empty response")
            save_string_to_file(json.dumps(_OBJECT_INFO, indent=2), _object_info_backup_path)
        except Exception as e:
            if type(e) != ComfyIsNotAvailable:
                saveLogError(e, "Error on object info download")
            if os.path.exists(_object_info_backup_path):
                print("*** object info has been loaded from backup")
                _OBJECT_INFO = json.loads(read_string_from_file(_object_info_backup_path))
            else:
                raise Exception(f"Unable to download object info, and backup doesn't exist") from None
    return _OBJECT_INFO


def getElementFieldInput(apiNode: dict) -> Field:
    type: DataType = None
    default = None
    for input, value in apiNode["inputs"].items():
        if input in ("file", "image"):
            if value:
                filename = value
                subfolder = ""
                if '/' in value:
                    filename = value.split('/')[-1]
                    subfolder = value.removesuffix(filename)
                default = ComfyFile(filename, subfolder, "input")
            if input == "image":
                type = DataType.IMAGE
            else:
                if default and default.getDataType() == DataType.IMAGE:
                    type = DataType.IMAGE
                type = DataType.VIDEO
            return Field(input, type, default)

    classInfo = objectInfo()[apiNode["class_type"]]
    for inputsDict in (classInfo["input"].get("required", {}), classInfo["input"].get("optional", {})):
        for input, inputInfo in inputsDict.items():
            if isinstance(inputInfo, list) and len(inputInfo) > 0:
                if inputInfo[0] == "STRING":
                    type = DataType.STRING
                elif inputInfo[0] == "INT":
                    type = DataType.INT
                elif inputInfo[0] == "FLOAT":
                    type = DataType.FLOAT
                else:
                    continue
                default = apiNode["inputs"].get(input, None)
                if default is not None:
                    return Field(input, type, default)


def getElementFieldOutput(apiNode: dict):
    classInfo = objectInfo()[apiNode["class_type"]]
    type, default = getNodeDataTypeAndValueLegacy(apiNode)
    field = Field("", type, default)
    return field

