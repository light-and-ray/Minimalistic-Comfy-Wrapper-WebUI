import json, os
from mcww import shared
from mcww.utils import read_string_from_file, save_string_to_file
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
    else:
        raise WorkflowIsNotSupported("This workflow contains 'PrimitiveNode'(s) of not either int, "
            "float, boolean, string type, which are not supported yet due to Comfy's bug. "
            f"The unsupported type is {primitiveType}")


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


def _getInputs(keys, graphNode, links, bypasses):
    inputs = {key : None for key in keys}
    linkToValue = {entry[0] : [str(entry[1]), entry[2]] for entry in links}
    widgetsValues = []
    if "widgets_values" in graphNode:
        for widgetsValue in graphNode["widgets_values"]:
            if widgetsValue in ("fixed", "increment", "decrement", "randomize", "image"): continue
            widgetsValues.append(widgetsValue)
        for i in range(len(widgetsValues)):
            inputs[keys[i]] = widgetsValues[i]

    for graphInput in graphNode["inputs"]:
        key = graphInput["name"]
        link = graphInput["link"]
        while link in bypasses:
            link = bypasses[link]
        if link is None:
            continue
        inputs[key] = linkToValue[link]

    return inputs


def graphToApi(graph):
    try:
        if graph["definitions"]["subgraphs"]:
            raise WorkflowIsNotSupported("This workflow contains subgraphs. "
                    "Workflows with subgraphs can't be converted into API format on fly yet. "
                    "To use this workflow in MCWW please convert it into API format manually")
    except (IndexError, KeyError, TypeError):
        pass
    api = dict()
    bypasses = dict()
    for graphNode in graph["nodes"]:
        if graphNode["type"] == "Reroute" or graphNode["mode"] == 4:
            try:
                bypasses[graphNode["outputs"][0]["links"][0]] = graphNode["inputs"][0]["link"]
            except (IndexError, KeyError, TypeError):
                pass

    for graphNode in graph["nodes"]:
        if graphNode["type"] == "PrimitiveNode":
            fixPrimitiveNode(graphNode)
        apiNode = dict()
        classInfo: dict|None = objectInfo().get(graphNode["type"])
        if not classInfo:
            if graphNode["type"] not in SUPPRESS_NODE_SKIPPING_WARNING:
                shared.workflowsLoadingContext.warning("Node type {} is absent in object info, skipping".format(graphNode["type"]))
            continue

        classInputsKeys = _getClassInputsKeys(classInfo)
        apiNode["inputs"] = _getInputs(classInputsKeys, graphNode, graph["links"], bypasses)

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
    import argparse
    parser = argparse.ArgumentParser(description='Convert workflow graph JSON to API JSON.')
    parser.add_argument('input', help='Path to input workflow graph JSON file')
    parser.add_argument('-o', '--output', help='Optional path for output API JSON file')
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    # Read the workflow graph from input file
    workflow_graph_str = read_string_from_file(input_path)
    workflow_graph = json.loads(workflow_graph_str)

    # Convert graph to API
    workflow_api = graphToApi(workflow_graph)
    workflow_api_str = json.dumps(workflow_api, indent=2)

    # Determine output file path
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base} API converted{ext}"

    # Save the API JSON to output file
    save_string_to_file(workflow_api_str, output_path)

    print(f"API JSON saved to: {output_path}")

