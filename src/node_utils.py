from enum import Enum
import json, re

class DataType(Enum):
    STRING = "string"
    FLOAT = "float"
    INT = "int"
    IMAGE = "image"
    VIDEO = "video"


def getNodeDataTypeAndValue(node: dict) -> DataType:
    try:
        node["inputs"]["image"]
        return DataType.IMAGE, None
    except KeyError:
        pass

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
