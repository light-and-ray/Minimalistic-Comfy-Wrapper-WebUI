from dataclasses import dataclass
from mcww.utils import DataType
from mcww.comfy.comfyFile import ComfyFile
import json, requests, os
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
from mcww import opts
from mcww.utils import DataType, read_string_from_file, save_string_to_file, saveLogError
from mcww.comfy.comfyFile import ComfyFile, getUploadedComfyFile
from mcww.comfy.comfyUtils import getHttpComfyPathUrl
from mcww.comfy.comfyAPI import ComfyIsNotAvailable


@dataclass
class Field:
    name: str
    type: DataType
    defaultValue: str


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


def _getMediaDefault(value: str):
    if value:
        filename = value
        subfolder = ""
        if '/' in value:
            filename = value.split('/')[-1]
            subfolder = value.removesuffix(filename)
        return ComfyFile(filename, subfolder, "input")


def _getElementFields(apiNode: dict, isInput: bool) -> list[Field]:
    fields = list[Field]()

    classInfo = objectInfo()[apiNode["class_type"]]
    for inputsDict in (classInfo["input"].get("required", {}), classInfo["input"].get("optional", {})):
        for input, inputInfo in inputsDict.items():
            if isinstance(inputInfo, list) and len(inputInfo) > 0:
                if isinstance(inputInfo[0], str) and inputInfo[0] != "COMBO":
                    if inputInfo[0] == "STRING":
                        type = DataType.STRING
                    elif inputInfo[0] == "INT":
                        type = DataType.INT
                    elif inputInfo[0] == "FLOAT":
                        type = DataType.FLOAT
                    elif not isInput and inputInfo[0] == "IMAGE":
                        type = DataType.IMAGE
                    elif not isInput and inputInfo[0] == "VIDEO":
                        type = DataType.VIDEO
                    else:
                        continue
                    default = apiNode["inputs"].get(input, None)
                    if default is not None or not isInput:
                        fields.append(Field(input, type, default))

                elif isinstance(inputInfo[0], str) and inputInfo[0] == "COMBO":
                    # new dropdown
                    if len(inputInfo) > 1 and isinstance(inputInfo[1], dict):
                        comboDict = inputInfo[1]
                        if isInput:
                            type = None
                            if comboDict.get("video_upload", False):
                                type = DataType.VIDEO
                            if comboDict.get("image_upload", False):
                                type = DataType.IMAGE
                            if type:
                                default = _getMediaDefault(apiNode["inputs"].get(input, None))
                                fields.append(Field(input, type, default))

                elif isinstance(inputInfo[0], list):
                    # old dropdown
                    if isInput and input in ("file", "image"): # upload widgets
                        default = _getMediaDefault(apiNode["inputs"].get(input, None))
                        if input == "image":
                            type = DataType.IMAGE
                        else:
                            if default and default.getDataType() == DataType.IMAGE:
                                type = DataType.IMAGE
                            type = DataType.VIDEO
                        fields.append(Field(input, type, default))
    return fields


def getElementField(apiNode: dict, isInput: bool) -> Field:
    fields = _getElementFields(apiNode, isInput)
    if not fields:
        return None
    priorityTypes = [DataType.IMAGE, DataType.VIDEO, DataType.STRING]
    for priorityType in priorityTypes:
        for field in fields:
            if field.type == priorityType:
                return field
    return fields[0]

