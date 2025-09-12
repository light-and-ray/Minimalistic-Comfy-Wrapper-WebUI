from settings import COMFY_ADDRESS
import requests, json

_OBJECT_INFO: dict|None = None
def objectInfo():
    global _OBJECT_INFO
    if _OBJECT_INFO is None:
        try:
            url = f"http://{COMFY_ADDRESS}/object_info"
            response = requests.get(url)
            response.raise_for_status()
            _OBJECT_INFO = response.json()
            if not _OBJECT_INFO:
                raise Exception("Empty response")
        except Exception as e:
            _OBJECT_INFO = None
            raise Exception(f"Unable to download object info: {e.__class__.__name__}: {e}")
    return _OBJECT_INFO


def _getClassInputsKeys(classInfo):
    classInputs = []
    required = classInfo["input_order"].get("required")
    optional = classInfo["input_order"].get("optional")
    if required:
        classInputs += required
    if optional:
        classInputs += optional
    widgetInputs = []
    nonWidgetInputs = []
    for classInput in classInputs:
        try:
            if (classInput in classInfo["input"]["required"] and 
                (
                    isinstance(classInfo["input"]["required"][classInput][0], list) or
                    len(classInfo["input"]["required"][classInput]) > 1 and
                    "default" in classInfo["input"]["required"][classInput][1]
                )
            ):
                widgetInputs.append(classInput)
            else:
                nonWidgetInputs.append(classInput)
        except Exception as e:
            print(e)
            print(classInput, classInfo["input"]["required"][classInput])
            raise
    classInputs = widgetInputs + nonWidgetInputs
    return classInputs


def _getInputs(keys, graphNode, links):
    inputs = {key : None for key in keys}
    linkToValue = {entry[0] : [str(entry[1]), entry[2]] for entry in links}
    widgetsValues = []
    for widgetsValue in graphNode["widgets_values"]:
        if widgetsValue in ("fixed", "increment", "decrement", "randomize", "image"): continue
        widgetsValues.append(widgetsValue)
    for i in range(len(widgetsValues)):
        inputs[keys[i]] = widgetsValues[i]
    
    for graphInput in graphNode["inputs"]:
        key = graphInput["name"]
        link = graphInput["link"]
        if link is None:
            del inputs[key]
            continue
        inputs[key] = linkToValue[link]
        
    return inputs


def graphToApi(graph):
    api = dict()
    for graphNode in graph["nodes"]:
        apiNode = dict()
        classInfo: dict|None = objectInfo().get(graphNode["type"])
        if not classInfo:
            print(f"Skipped {graphNode["type"]} during conversion")
            continue

        classInputsKeys = _getClassInputsKeys(classInfo)
        apiNode["inputs"] = _getInputs(classInputsKeys, graphNode, graph["links"])

        apiNode["class_type"] = graphNode["type"]

        apiNode["_meta"] = dict()
        if graphNode.get("title") is not None:
            apiNode["_meta"]["title"] = graphNode["title"]
        elif classInfo["display_name"]:
            apiNode["_meta"]["title"] = classInfo["display_name"]
        else:
            apiNode["_meta"]["title"] = classInfo["name"]

        api[graphNode["id"]] = apiNode

    sorted_keys = sorted(api.keys())
    sorted_api = {key: api[key] for key in sorted_keys}

    return sorted_api


if __name__ == "__main__":
    with open("../workflows/wan2_2_flf2v.json") as f:
        workflowGraphStr = f.read()
    workflowGraph = json.loads(workflowGraphStr)

    workflowAPI = graphToApi(workflowGraph)
    
    from utils import save_string_to_file
    workflowAPIStr = json.dumps(workflowAPI, indent=2)
    save_string_to_file(workflowAPIStr, "../workflows/wan2_2_flf2v API generated.json")
    
    with open("../workflows/wan2_2_flf2v API.json") as f:
        workflowGraphAPIOriginalStr = f.read()
    workflowGraphAPIOriginal = json.loads(workflowGraphAPIOriginalStr)
    workflowGraphAPIOriginalStr = json.dumps(workflowGraphAPIOriginal, indent=2)
    print(f"TEST RESULT: {workflowGraphAPIOriginalStr == workflowAPIStr}")
