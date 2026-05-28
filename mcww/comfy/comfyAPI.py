import requests
import time, json
import urllib.parse
from mcww import opts, shared
from mcww.utils import saveLogError, saveLogJson, cleanupTerminalOutputs
from mcww.comfy.comfyUtils import ( getHttpComfyPathUrl, isComfyIsNotAvailable, tryGetJsonFromURL,
    checkForComfyIsNotAvailable, ComfyIsNotAvailable, postJson,
)
from mcww.comfy.comfyFile import ComfyFile

class ComfyUIException(Exception):
    pass

class ComfyUIInterrupted(Exception):
    pass

class UnqueuedByComfyUI(Exception):
    pass

ComfyIsNotAvailable


def _enqueueComfyInner(prompt, prompt_id):
    url = getHttpComfyPathUrl("/prompt")
    payload = {
        "prompt": prompt,
        "client_id": shared.clientID,
        "prompt_id": prompt_id,
    }
    try:
        return postJson(url, payload, increasedTimeout=True)
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 400:
            try:
                error_data = e.response.json()
                saveLogJson(error_data, "invalid_workflow_response")
                error_display = f"\n\n```json\n{json.dumps(error_data, indent=2)}\n\n```"
            except json.JSONDecodeError:
                error_display = e.response.text
            saveLogJson(prompt, "invalid_workflow")
            raise ComfyUIException(f"Error on queueing: {error_display}")
        raise e


def _getHistory(prompt_id) -> dict | None:
    response = tryGetJsonFromURL(getHttpComfyPathUrl(f"/history/{prompt_id}"), increasedTimeout=True)
    if response and prompt_id in response:
        return response[prompt_id]
    return None


def _getQueue(prompt_id) -> dict | None:
    queueAll = tryGetJsonFromURL(getHttpComfyPathUrl(f"/queue"), increasedTimeout=True)
    for entry in queueAll["queue_running"] + queueAll["queue_pending"]:
        if entry[1] == prompt_id:
            return entry
    return None


def _getResultsInner(prompt_id: str) -> dict | None:
    if _getQueue(prompt_id): return
    outputsByNode = {}
    history = _getHistory(prompt_id)
    if not history:
        raise UnqueuedByComfyUI("No prompt_id in history. Maybe ComfyUI has been restarted, or the task(s) were unqueued inside ComfyUI")
    status = history["status"]["status_str"]

    if status == "error":
        for message in history["status"]["messages"]:
            if message[0] == "execution_error":
                saveLogJson(history, "execution_error_history")
                raise ComfyUIException(message[1]["exception_type"] + ": " + message[1]["exception_message"])
            if message[0] == "execution_interrupted":
                raise ComfyUIInterrupted("Execution was interrupted")
    elif status != "success":
        print(json.dumps(history["status"], indent=2))
        raise Exception(f"Unknown ComfyUI status: {status}")

    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        outputsInNode = []
        for field in ('images', 'audio'): # video is also inside images field
            if field in node_output:
                for file in node_output[field]:
                    comfyFile = ComfyFile(
                        filename=file['filename'],
                        subfolder=file['subfolder'],
                        folder_type=file['type']
                    )
                    outputsInNode.append(comfyFile)
        if 'text' in node_output:
            outputsInNode.extend(node_output['text'])

        outputsByNode[node_id] = outputsInNode

    return outputsByNode


def getResultsIfPossible(prompt_id: str) -> dict | None:
    try:
        nodes: dict | None = _getResultsInner(prompt_id)
        return nodes
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def enqueueComfy(workflow: str, prompt_id):
    try:
        _enqueueComfyInner(workflow, prompt_id)
        time.sleep(0.2)
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def getWorkflows():
    try:
        workflowsDataUrl = getHttpComfyPathUrl("/userdata?dir=workflows&recurse=true&split=false&full_info=true")
        workflowsData = tryGetJsonFromURL(workflowsDataUrl)
        if not workflowsData:
            return {}

        workflows = dict[str, dict]()
        for workflowData in workflowsData:
            path: str = workflowData["path"]
            if not path.startswith(opts.MCWW_WORKFLOWS_SUBDIR):
                continue
            if not path.endswith('.json'):
                continue
            try:
                workflowUrl = getHttpComfyPathUrl("/userdata/{}".format(
                    urllib.parse.quote("workflows/" + path, safe=[])
                ))
                workflow = tryGetJsonFromURL(workflowUrl)
                if workflow:
                    workflows[path] = workflow
                else:
                    print(f"*** 404 error while getting '{path}'")
            except Exception as e:
                checkForComfyIsNotAvailable(e)
                saveLogError(e, f"Error on receiving '{path}' workflow")

        return workflows
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def getConsoleLogs():
    try:
        logs = tryGetJsonFromURL(getHttpComfyPathUrl("/internal/logs/raw"))
        logs = "".join([x["m"] for x in logs["entries"]])
        logs = cleanupTerminalOutputs(logs)
        return logs
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def interruptComfy(prompt_id: str):
    try:
        url = getHttpComfyPathUrl('/interrupt')
        data = {"prompt_id": prompt_id}
        postJson(url, data, increasedTimeout=True)
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def unQueueComfy(prompt_id: str):
    try:
        url = getHttpComfyPathUrl('/queue')
        payload = {
            "delete": [prompt_id]
        }
        postJson(url, payload, increasedTimeout=True)
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def _restartComfyManagerV3():
    restartUrl = getHttpComfyPathUrl("/manager/reboot")
    response = requests.get(restartUrl, timeout=opts.REQUESTS_TIMEOUT_NORMAL)
    response.raise_for_status()

def _restartComfyManagerV4():
    restartUrl = getHttpComfyPathUrl("/manager/reboot")
    postJson(restartUrl, None)

def _restartComfyManagerV4_2():
    restartUrl = getHttpComfyPathUrl("/api/v2/manager/reboot")
    postJson(restartUrl, None)

def restartComfy():
    restartFunctions = [
        _restartComfyManagerV4,
        _restartComfyManagerV3,
        _restartComfyManagerV4_2,
    ]

    for i, restartFunction in enumerate(restartFunctions):
        try:
            restartFunction()
            return
        except requests.exceptions.HTTPError as e:
            isFallbackError = e.response is not None and e.response.status_code in (404, 405)
            hasMoreVersions = i < len(restartFunctions) - 1

            if isFallbackError and hasMoreVersions:
                continue
            else:
                checkForComfyIsNotAvailable(e)
                raise
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            raise
        except Exception as e:
            checkForComfyIsNotAvailable(e)
            raise


def getLoras() -> list[str]:
    try:
        loras = tryGetJsonFromURL(getHttpComfyPathUrl("/models/loras"))
        return loras
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def getStats() -> dict:
    try:
        stats = tryGetJsonFromURL(getHttpComfyPathUrl("/system_stats"))
        return stats
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def freeCacheAndMemory():
    try:
        url = getHttpComfyPathUrl('/free')
        payload = {
            "unload_models": True,
            "free_memory": True,
        }
        postJson(url, payload)
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise


def waitForComfy(timeout: float):
    testUrl = getHttpComfyPathUrl("/models/loras")
    start_time = time.time()
    poll_interval = 0.5

    while True:
        try:
            response = requests.get(testUrl, timeout=2)
            if response.status_code == 200:
                return True
        except Exception as e:
            if not isComfyIsNotAvailable(e):
                raise

        if time.time() - start_time > timeout:
            print(f"Timeout reached: ComfyUI server did not respond within {timeout} seconds.")
            return False

        time.sleep(poll_interval)
