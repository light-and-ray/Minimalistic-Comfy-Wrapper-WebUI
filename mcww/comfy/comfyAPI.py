import urllib.request, urllib.error
import websocket, uuid, json
import urllib.parse
from mcww import opts
from mcww.utils import saveLogJson
from mcww.comfy.comfyUtils import getHttpComfyPathUrl, getWsComfyPathUrl
from mcww.comfy.comfyFile import ComfyFile

client_id = str(uuid.uuid4())

class ComfyUIException(Exception):
    pass


def queue_prompt(prompt, prompt_id):
    try:
        p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(getHttpComfyPathUrl("/prompt"), data=data)
        urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        if e.code == 400:
            saveLogJson(prompt, "invalid_workflow")
            raise ComfyUIException("Error queueing prompt, there is a problem with workflow. "
                "Check invalid_workflow in log directory")
        raise


def get_history(prompt_id):
    with urllib.request.urlopen(getHttpComfyPathUrl(f"/history/{prompt_id}")) as response:
        return json.loads(response.read())


def get_images(ws, prompt):
    prompt_id = str(uuid.uuid4())
    queue_prompt(prompt, prompt_id)
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done

    history = get_history(prompt_id)[prompt_id]
    status = history["status"]["status_str"]


    if status == "error":
        for message in history["status"]["messages"]:
            if message[0] == "execution_error":
                saveLogJson(history, "execution_error_history")
                saveLogJson(prompt, "execution_error_workflow")
                raise ComfyUIException(message[1]["exception_type"] + ": " + message[1]["exception_message"])
    elif status != "success":
        print(json.dumps(history["status"], indent=2))
        raise Exception(f"Unknown ComfyUI status: {status}")


    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                comfyFile = ComfyFile(
                    filename=image['filename'],
                    subfolder=image['subfolder'],
                    folder_type=image['type']
                )
                images_output.append(comfyFile)
        output_images[node_id] = images_output

    return output_images



def processComfy(workflow: str) -> dict:
    ws = websocket.WebSocket()
    ws.connect(getWsComfyPathUrl(f"/ws?clientId={client_id}"))
    nodes = get_images(ws, workflow)
    ws.close()
    return nodes


def getWorkflows():
    workflowsDataUrl = getHttpComfyPathUrl("/userdata?dir=workflows&recurse=true&split=false&full_info=true")
    with urllib.request.urlopen(workflowsDataUrl) as response:
        workflowsData = json.loads(response.read())
    workflows = dict[str, dict]()
    for workflowData in workflowsData:
        path: str = workflowData["path"]
        if not path.startswith(opts.MCWW_WORKFLOWS_SUBDIR):
            continue
        workflowUrl = getHttpComfyPathUrl("/userdata/{}".format(
            urllib.parse.quote("workflows/" + path, safe=[])
        ))
        with urllib.request.urlopen(workflowUrl) as response:
            workflow = response.read()
        workflows[path] = workflow
    return workflows
