import requests, json, os
from mcww.utils import read_string_from_file, save_string_to_file
from mcww import opts

_object_info_backup_path = os.path.join(opts.MCWW_DIRECTORY, "..", "object_info_backup.json")

_OBJECT_INFO: dict|None = None
def objectInfo():
    global _OBJECT_INFO
    if _OBJECT_INFO is None:
        try:
            url = f"http://{opts.COMFY_ADDRESS}/object_info"
            response = requests.get(url)
            response.raise_for_status()
            _OBJECT_INFO = response.json()
            if not _OBJECT_INFO:
                raise Exception("Empty response")
            save_string_to_file(json.dumps(_OBJECT_INFO, indent=2), _object_info_backup_path)
        except Exception as e:
            if os.path.exists(_object_info_backup_path):
                print("*** object info has been loaded from backup")
                _OBJECT_INFO = json.loads(read_string_from_file(_object_info_backup_path))
            else:
                raise Exception(f"Unable to download object info, and backup doesn't exist") from None
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
                    ("default" in classInfo["input"]["required"][classInput][1] or
                    "multiline" in classInfo["input"]["required"][classInput][1])
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
            continue
        inputs[key] = linkToValue[link]

    return inputs


def graphToApi(graph):
    api = dict()
    for graphNode in graph["nodes"]:
        apiNode = dict()
        classInfo: dict|None = objectInfo().get(graphNode["type"])
        if not classInfo:
            if graphNode["type"] not in opts.SUPPRESS_NODE_SKIPPING_WARNING:
                print("Skipped {} during conversion".format(graphNode["type"]))
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
    import argparse
    import json
    import os
    from mcww.utils import save_string_to_file, read_string_from_file

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

