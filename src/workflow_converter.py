from settings import COMFY_ADDRESS
import requests, json
from utils import natural_sort_key

def downloadObjectInfo() -> dict:
    url = f"http://{COMFY_ADDRESS}/object_info"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
    
OBJECT_INFO: dict|None = None

def graphToApi(graph):
    global OBJECT_INFO
    if OBJECT_INFO is None:
        OBJECT_INFO = downloadObjectInfo()
    api = dict()
    for graphNode in graph["nodes"]:
        apiNode = dict()
        classInfo = OBJECT_INFO.get(graphNode["type"])
        if not classInfo:
            print(f"Skipped {graphNode["type"]} during converting")
            continue

        apiNode["inputs"] = dict()
        classInputs = classInfo["input_order"]["required"]
        for classInput in classInputs:
            apiNode["inputs"][classInput] = None

        apiNode["class_type"] = graphNode["type"]

        apiNode["_meta"] = dict()
        if graphNode.get("title") is not None:
            apiNode["_meta"]["title"] = graphNode["title"]
        else:
            apiNode["_meta"]["title"] = classInfo["display_name"]

        api[graphNode["id"]] = apiNode

    sorted_keys = sorted(api.keys())
    sorted_api = {key: api[key] for key in sorted_keys}

    return sorted_api

if __name__ == "__main__":
    with open("../workflows/wan2_2_flf2v.json") as f:
        workflowGraph = f.read()
    workflowGraph = json.loads(workflowGraph)
    workflowAPI = graphToApi(workflowGraph)
    from utils import save_string_to_file
    workflowAPI = json.dumps(workflowAPI, indent=4)
    save_string_to_file(workflowAPI, "../workflows/wan2_2_flf2v API generated.json")

