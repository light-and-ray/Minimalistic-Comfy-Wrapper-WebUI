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

class ComfyUIInterrupted(Exception):
    pass

ComfyIsNotAvailable


def _enqueueComfyInner(prompt, prompt_id):
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


def _getHistory(prompt_id) -> dict | None:
    with urllib.request.urlopen(getHttpComfyPathUrl(f"/history/{prompt_id}")) as response:
        responseStr = response.read()
    if responseStr:
        responseObj = json.loads(responseStr)
        if responseObj and prompt_id in responseObj:
            return responseObj[prompt_id]
    return None


def _getQueue(prompt_id) -> dict | None:
    with urllib.request.urlopen(getHttpComfyPathUrl(f"/queue")) as response:
        queueAll = json.loads(response.read())
    for entry in queueAll["queue_running"] + queueAll["queue_pending"]:
        if entry[1] == prompt_id:
            return entry
    return None


def _getResultsInner(prompt, prompt_id: str) -> dict | None:
    if _getQueue(prompt_id): return
    output_images = {}
    history = _getHistory(prompt_id)
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
            if message[0] == "execution_interrupted":
                raise ComfyUIInterrupted("Execution was interrupted")
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


def getResultsIfPossible(workflow: str, prompt_id: str) -> dict | None:
    try:
        nodes: dict | None = _getResultsInner(workflow, prompt_id)
        return nodes
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def enqueueComfy(workflow: str) -> dict:
    try:
        prompt_id = str(uuid.uuid4())
        _enqueueComfyInner(workflow, prompt_id)
        time.sleep(0.2)
        return prompt_id
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


def interruptComfy(prompt_id: str):
    try:
        url = getHttpComfyPathUrl('/interrupt')
        data = {"prompt_id": prompt_id}
        data_bytes = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            url=url, data=data_bytes, method='POST',
            headers={
                'Content-Type': 'application/json',
                'Content-Length': len(data_bytes),
            },
        )
        with urllib.request.urlopen(request) as response:
            pass
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def unQueueComfy(prompt_id: str):
    try:
        url = getHttpComfyPathUrl('/queue')
        payload = {
            "delete": [prompt_id]
        }
        json_data = json.dumps(payload)
        data = json_data.encode('utf-8')
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': len(data),
            },
            method='POST'
        )
        with urllib.request.urlopen(request) as response:
            pass
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def restartComfy():
    try:
        restartUrl = getHttpComfyPathUrl("/manager/reboot")
        with urllib.request.urlopen(restartUrl) as response:
            pass
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise
