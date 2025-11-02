import urllib.request, urllib.error
import time, uuid, json
import urllib.parse
from mcww import opts
from mcww.utils import saveLogJson
from mcww.comfy.comfyUtils import ( getHttpComfyPathUrl,
    checkForComfyIsNotAvailable, ComfyIsNotAvailable
)
from mcww.comfy.comfyFile import ComfyFile

client_id = str(uuid.uuid4())

class ComfyUIException(Exception):
    pass

ComfyIsNotAvailable

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


def get_history(prompt_id) -> dict | None:
    with urllib.request.urlopen(getHttpComfyPathUrl(f"/history/{prompt_id}")) as response:
        responseStr = response.read()
    if responseStr:
        responseObj = json.loads(responseStr)
        if responseObj and prompt_id in responseObj:
            return responseObj[prompt_id]
    return None


def get_queue(prompt_id) -> dict | None:
    with urllib.request.urlopen(getHttpComfyPathUrl(f"/queue")) as response:
        queueAll = json.loads(response.read())
    for entry in queueAll["queue_running"] + queueAll["queue_pending"]:
        if entry[1] == prompt_id:
            return entry
    return None


def get_images(prompt):
    prompt_id = str(uuid.uuid4())
    queue_prompt(prompt, prompt_id)
    time.sleep(0.2)
    output_images = {}
    while get_queue(prompt_id):
        time.sleep(0.050)
    history = get_history(prompt_id)
    if not history:
        saveLogJson(prompt, "empty_history_workflow")
        raise ComfyUIException("No prompt_id in history. Maybe it was removed from the internal comfy queue")
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
    try:
        nodes = get_images(workflow)
        return nodes
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def getWorkflows():
    try:
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
                workflow = json.loads(response.read())
            workflows[path] = workflow
        return workflows
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def getConsoleLogs():
    try:
        logsUrl = getHttpComfyPathUrl("/internal/logs")
        with urllib.request.urlopen(logsUrl) as response:
            logs = json.loads(response.read())
        return logs
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


