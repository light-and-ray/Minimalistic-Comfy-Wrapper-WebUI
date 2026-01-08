import json, os
from mcww import shared
from mcww.utils import read_string_from_file, save_string_to_file, natural_sort_key
from mcww.comfy.nodeUtils import objectInfo


class WorkflowIsNotSupported(Exception):
    pass


SUPPRESS_NODE_SKIPPING_WARNING: set[str] = set([
        "MarkdownNote",
        "Note",
        "Reroute",
    ])


def fixPrimitiveNode(graphNode: dict):
    primitiveType = graphNode["outputs"][0]["type"]
    if primitiveType == "INT":
        graphNode["type"] = "PrimitiveInt"
    elif primitiveType == "STRING":
        graphNode["type"] = "PrimitiveString"
    elif primitiveType == "BOOLEAN":
        graphNode["type"] = "PrimitiveBoolean"
    elif primitiveType == "FLOAT":
        graphNode["type"] = "PrimitiveFloat"
    elif primitiveType == "*":
        return True
    else:
        raise WorkflowIsNotSupported("This workflow contains 'PrimitiveNode'(s) of not either int, "
            "float, boolean, string type, which are not supported yet due to Comfy's bug. "
            f"The unsupported type is {primitiveType}")
    return False


def isWidgetInputInfo(inputInfo: list):
    if isinstance(inputInfo[0], list):
        return True # dropdown
    if len(inputInfo) > 1 and isinstance(inputInfo[1], dict):
        type_ = inputInfo[0]
        obj = inputInfo[1]
        if type_ in ("STRING", "INT", "FLOAT", "BOOLEAN"):
            return True # INT FLOAT etc
        if type_ == "COMBO":
            if "options" in obj:
                return True # dropdown


def _getClassInputsKeys(classInfo):
    classInputs = []
    required = classInfo["input_order"].get("required", [])
    optional = classInfo["input_order"].get("optional", [])
    classInputs += required
    classInputs += optional
    widgetInputs = []
    nonWidgetInputs = []
    for classInput in classInputs:
        try:
            if required and classInput in classInfo["input"]["required"]:
                inputInfo = classInfo["input"]["required"][classInput]
            elif optional:
                inputInfo = classInfo["input"]["optional"][classInput]
            else:
                inputInfo = None
            if inputInfo and isWidgetInputInfo(inputInfo):
                widgetInputs.append(classInput)
            else:
                nonWidgetInputs.append(classInput)
        except Exception as e:
            print(e)
            # print(classInput, classInfo["input"]["required"][classInput])
            raise
    classInputs = widgetInputs + nonWidgetInputs
    return classInputs


def _getSubgraphInputsKeys(subgraph, graphNode):
    result = []
    widgetInputs = [x[1] for x in graphNode["properties"].get("proxyWidgets", [])]
    nonWidgetInputs = []
    for subgraphInput in subgraph["inputs"]:
        if subgraphInput["name"] not in widgetInputs:
            nonWidgetInputs.append(subgraphInput["name"])
    result = widgetInputs + nonWidgetInputs
    return result


def _getInputs(keys: list[str], graphNode: dict, linkToValue: dict, bypasses: dict):
    inputs = {key : None for key in keys}
    widgetsValues = []
    if "widgets_values" in graphNode:
        for widgetsValue in graphNode["widgets_values"]:
            if widgetsValue in ("fixed", "increment", "decrement", "randomize", "image"): continue
            widgetsValues.append(widgetsValue)
        for i in range(len(widgetsValues)):
            try:
                inputs[keys[i]] = widgetsValues[i]
            except:
                print("index:", i)
                print("keys:", keys)
                print("widgetsValues:", widgetsValues)
                print(json.dumps(graphNode, indent=2))
                raise

    for graphInput in graphNode["inputs"]:
        key = graphInput["name"]
        link = graphInput["link"]
        while link in bypasses:
            link = bypasses[link]
        if link is None:
            continue
        inputs[key] = linkToValue[link]

    return inputs


def _getBypasses(nodes: list):
    bypasses = dict()
    for node in nodes:
        if node["type"] == "Reroute" or node["mode"] == 4:
            try:
                for outputLink in node["outputs"][0]["links"]:
                    bypasses[outputLink] = node["inputs"][0]["link"]
            except (IndexError, KeyError, TypeError):
                pass
    return bypasses


def _getLinkToValue(links: list):
    if isinstance(links[0], list):
        linkToValue = {entry[0] : [str(entry[1]), entry[2]] for entry in links}
    else: # dict
        linkToValue = {entry['id'] : [str(entry['origin_id']), entry['origin_slot']] for entry in links}
    return linkToValue


def _applySubgraphInputsLinkToValue(linkToValue: dict, subgraphNodeId: str|int, subgraphInputs: dict, subgraphInputNodeId: str):
    for key in linkToValue.keys():
        if linkToValue[key][0] != subgraphInputNodeId:
            linkToValue[key][0] = f"{subgraphNodeId}:{linkToValue[key][0]}"
        else:
            linkToValue[key] = list(subgraphInputs.values())[linkToValue[key][1]]


def _applySubgraphOutputsLinkToValue(linkToValue: dict, subgraphOutputs: dict):
    for key in linkToValue.keys():
        nodeId = linkToValue[key][0]
        slot = linkToValue[key][1]
        if nodeId in subgraphOutputs:
            linkToValue[key] = subgraphOutputs[nodeId][slot]


def _graphToApiOneNode(graphNode: dict, bypasses: dict, linkToValue: dict):
    if graphNode["type"] == "PrimitiveNode":
        needSkip = fixPrimitiveNode(graphNode)
        if needSkip:
            return None
    apiNode = dict()
    classInfo: dict|None = objectInfo().get(graphNode["type"])
    if not classInfo:
        if graphNode["type"] not in SUPPRESS_NODE_SKIPPING_WARNING:
            shared.workflowsLoadingContext.warning("Node type {} is absent in object info, skipping".format(graphNode["type"]))
        return None

    classInputsKeys = _getClassInputsKeys(classInfo)
    apiNode["inputs"] = _getInputs(classInputsKeys, graphNode, linkToValue, bypasses)

    apiNode["class_type"] = graphNode["type"]

    apiNode["_meta"] = dict()
    if graphNode.get("title") is not None:
        apiNode["_meta"]["title"] = graphNode["title"]
    elif classInfo["display_name"]:
        apiNode["_meta"]["title"] = classInfo["display_name"]
    else:
        apiNode["_meta"]["title"] = classInfo["name"]
    return apiNode


def graphToApi(graph):
    subgraphs = dict[str, dict]()
    try:
        if graph["definitions"]["subgraphs"]:
            for object in graph["definitions"]["subgraphs"]:
                subgraphs[object["id"]] = object
    except (IndexError, KeyError, TypeError):
        pass
    api = dict()

    subgraphOutputs = dict[str, list[list]]()
    for graphNode in graph["nodes"]:
        if graphNode["type"] in subgraphs:
            subgraph = subgraphs[graphNode["type"]]
            subgraphLinkToValue = _getLinkToValue(subgraph["links"])
            outputs: list[list] = []
            for output in subgraph["outputs"]:
                output = subgraphLinkToValue[output["linkIds"][0]]
                output[0] = "{}:{}".format(graphNode['id'], output[0])
                outputs.append(output)
            subgraphOutputs[str(graphNode["id"])] = outputs

    graphBypasses = _getBypasses(graph["nodes"])
    graphLinkToValue = _getLinkToValue(graph["links"])
    _applySubgraphOutputsLinkToValue(graphLinkToValue, subgraphOutputs)

    for graphNode in graph["nodes"]:
        if graphNode["type"] not in subgraphs:
            apiNode = _graphToApiOneNode(graphNode, graphBypasses, graphLinkToValue)
            if apiNode is None: continue
            api[str(graphNode["id"])] = apiNode
        else:
            subgraph = subgraphs[graphNode["type"]]
            subgraphBypasses = _getBypasses(subgraph["nodes"])
            inputKeysSubgraphSort = [x["name"] for x in subgraph["inputs"]]
            inputKeysWidgetSort = _getSubgraphInputsKeys(subgraph, graphNode)
            subgraphInputs = _getInputs(inputKeysWidgetSort, graphNode, graphLinkToValue, graphBypasses)
            subgraphInputs = {key: subgraphInputs[key] for key in inputKeysSubgraphSort}
            subgraphLinkToValue = _getLinkToValue(subgraph["links"])
            _applySubgraphInputsLinkToValue(subgraphLinkToValue, graphNode["id"], subgraphInputs,
                    str(subgraph["inputNode"]["id"]))

            for subgraphNode in subgraph["nodes"]:
                if subgraphNode["type"] in subgraphs:
                    raise WorkflowIsNotSupported("This workflow contains nested subgraphs that are not supported yet. "
                        "Please convert this workflow into API format")
                apiNode = _graphToApiOneNode(subgraphNode, subgraphBypasses, subgraphLinkToValue)
                if apiNode is None: continue
                api["{}:{}".format(graphNode["id"], subgraphNode["id"])] = apiNode

    def sortKey(key: str):
        key = key.split(":")[0]
        return natural_sort_key(key)

    sorted_keys = sorted(api.keys(), key=sortKey)
    sorted_api = {key: api[key] for key in sorted_keys}

    return sorted_api


if __name__ == "__main__":
    import argparse
    from mcww.comfy.workflow import Workflow
    parser = argparse.ArgumentParser(description='Convert workflow graph JSON to API JSON.')
    parser.add_argument('input', help='Path to input workflow graph JSON file')
    args = parser.parse_args()

    input_path = args.input

    workflow_graph = json.loads(read_string_from_file(input_path))
    workflow_api = graphToApi(workflow_graph)
    workflow_parsed = Workflow(workflow_graph).getWorkflowDictCopy()

    base, ext = os.path.splitext(input_path)

    save_string_to_file(json.dumps(workflow_api, indent=2), f"{base} API converted{ext}")
    save_string_to_file(json.dumps(workflow_parsed, indent=2), f"{base} parsed{ext}")

