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


class DynamicField:
    def __init__(self, name: str, options: dict):
        self._name = name
        self._options = options

    def getFields(self, value):
        inputs = []
        for option in self._options:
            if option["key"] != value: continue
            inputs = list(option["inputs"].get("required", {}).keys())
            inputs += list(option["inputs"].get("optional", {}).keys())
            break
        result = [self._name] + [f"{self._name}.{x}" for x in inputs]
        return result


def getIsWidgetAndField(inputName: str, inputInfo: list|None):
    if not inputInfo:
        return False, inputName
    if isinstance(inputInfo[0], list):
        return True, inputName # dropdown
    if len(inputInfo) > 1 and isinstance(inputInfo[1], dict):
        type_ = inputInfo[0]
        obj = inputInfo[1]
        if type_ in ("STRING", "INT", "FLOAT", "BOOLEAN"):
            return True, inputName # INT FLOAT etc
        if type_ == "COMBO":
            if "options" in obj:
                return True, inputName # dropdown
        if type_ == "COMFY_DYNAMICCOMBO_V3":
            if "options" in obj:
                return True, DynamicField(inputName, obj["options"])
    return False, inputName


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
            isWidget, field = getIsWidgetAndField(classInput, inputInfo)
            if isWidget:
                widgetInputs.append(field)
            else:
                nonWidgetInputs.append(field)
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


def _getInputs(keys: list[str|DynamicField], graphNode: dict, linkToValue: dict, bypasses: dict):
    inputs = {key : None for key in keys if isinstance(key, str)}
    widgetsValues = []
    if "widgets_values" in graphNode:
        for widgetsValue in graphNode["widgets_values"]:
            if widgetsValue in ("fixed", "increment", "decrement", "randomize", "image"): continue
            widgetsValues.append(widgetsValue)
        i = 0
        while True:
            if i >= len(keys): break
            key = keys[i]
            if isinstance(key, str):
                if i >= len(widgetsValues): break
                inputs[key] = widgetsValues[i]
                i += 1
            elif isinstance(key, DynamicField):
                if i >= len(widgetsValues): break
                dynamicKeys = key.getFields(widgetsValues[i])
                for dynamicKey in dynamicKeys:
                    if i >= len(widgetsValues): break
                    inputs[dynamicKey] = widgetsValues[i]
                    i += 1
            else:
                raise Exception("Wrong key type")

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


def _getLinkToValue(links: list, parentNodeId: str):
    def addParentSuffix(id):
        newId = parentNodeId + ":" + str(id)
        newId = newId.removeprefix(':')
        return newId
    if isinstance(links[0], list):
        linkToValue = {link[0] : [addParentSuffix(link[1]), link[2]] for link in links}
    else: # dict
        linkToValue = {link['id'] : [addParentSuffix(link['origin_id']), link['origin_slot']] for link in links}
    return linkToValue


def _applySubgraphInputsLinkToValue(linkToValue: dict, subgraphInputs: dict, constInputNodeId: str):
    for key in linkToValue.keys():
        if linkToValue[key][0] != constInputNodeId:
            linkToValue[key][0] = linkToValue[key][0]
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

    def processNodes(nodes: list, links: list, parentNodeId: str, parentLinkToValue: dict, constInputNodeId: str|None):
        subgraphOutputs = dict[str, list[list]]()
        for node in nodes:
            nodeId: str = parentNodeId + ":" + str(node['id'])
            nodeId= nodeId.removeprefix(":")
            if node["type"] in subgraphs:
                subgraph = subgraphs[node["type"]]
                subgraphLinkToValue = _getLinkToValue(subgraph["links"], nodeId)
                outputs: list[list] = []
                for output in subgraph["outputs"]:
                    output = subgraphLinkToValue[output["linkIds"][0]]
                    outputs.append(output)
                subgraphOutputs[nodeId] = outputs

        graphBypasses = _getBypasses(nodes)
        graphLinkToValue = _getLinkToValue(links, parentNodeId)
        _applySubgraphOutputsLinkToValue(graphLinkToValue, subgraphOutputs)
        if constInputNodeId:
            for key, value in parentLinkToValue.items():
                if key in graphLinkToValue and graphLinkToValue[key][0] == constInputNodeId:
                    graphLinkToValue[key] = value

        for node in nodes:
            nodeId: str = parentNodeId + ":" + str(node['id'])
            nodeId= nodeId.removeprefix(":")
            if node["type"] not in subgraphs:
                apiNode = _graphToApiOneNode(node, graphBypasses, graphLinkToValue)
                if apiNode is None: continue
                api[nodeId] = apiNode
            else:
                subgraph = subgraphs[node["type"]]
                inputKeysSubgraphSort = [x["name"] for x in subgraph["inputs"]]
                inputKeysWidgetSort = _getSubgraphInputsKeys(subgraph, node)
                subgraphInputs = _getInputs(inputKeysWidgetSort, node, graphLinkToValue, graphBypasses)
                subgraphInputs = {key: subgraphInputs[key] for key in inputKeysSubgraphSort}
                subgraphLinkToValue = _getLinkToValue(subgraph["links"], nodeId)
                constInputNodeId = nodeId + ":" + str(subgraph["inputNode"]["id"])
                constInputNodeId = constInputNodeId.removeprefix(":")
                _applySubgraphInputsLinkToValue(subgraphLinkToValue, subgraphInputs, constInputNodeId)
                processNodes(subgraph["nodes"], subgraph["links"], nodeId, subgraphLinkToValue, constInputNodeId)

    processNodes(graph["nodes"], graph["links"], "", {}, None)

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
    # workflow_parsed = Workflow(workflow_graph).getWorkflowDictCopy()

    base, ext = os.path.splitext(input_path)

    save_string_to_file(json.dumps(workflow_api, indent=2), f"{base} API converted{ext}")
    # save_string_to_file(json.dumps(workflow_parsed, indent=2), f"{base} parsed{ext}")

