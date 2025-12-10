from dataclasses import dataclass
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
from mcww import queueing, shared
import asyncio, json


@dataclass
class ProgressBar:
    total_progress_max: int
    total_progress_current: int
    node_progress_max: int|None
    node_progress_current: int|None

g_lastProgressBar: str|None = None
g_lastTotalCachedNodes = 0


async def progressBarUpdates():
    def toPayload(obj: ProgressBar|None):
        if isinstance(obj, ProgressBar):
            obj = {
                "total_progress_max": obj.total_progress_max,
                "total_progress_current": obj.total_progress_current,
                "node_progress_max": obj.node_progress_max,
                "node_progress_current": obj.node_progress_current,
            }
        payload =  f"data: {json.dumps(obj)}\n\n"
        return payload

    global g_lastProgressBar
    if isinstance(g_lastProgressBar, str):
        yield g_lastProgressBar

    toYield = asyncio.Queue()

    def messageReceivedCallback(message: dict):
        global g_lastTotalCachedNodes
        if message.get('type') == 'status':
            asyncio.run(toYield.put(toPayload(None)))
        if message.get('type') == "execution_start":
            g_lastTotalCachedNodes = 0
        if message.get('type') == "execution_cached":
            g_lastTotalCachedNodes = len(message["data"]["nodes"])

        processing = queueing.queue.getInProgressProcessing()
        messagePromptId = message.get('data', {}).get('prompt_id', None)

        if processing:
            if messagePromptId == processing.prompt_id:
                if message.get('type') == "progress_state":
                    nodeValue = None
                    nodeMax = None
                    finishedNodes = 0
                    hasRunning = False
                    for node in message["data"]["nodes"].values():
                        if node['state'] == 'running':
                            nodeValue = node.get('value', None)
                            nodeMax = node.get('max', None)
                            hasRunning = True
                        else:
                            finishedNodes += 1
                    if hasRunning:
                        if nodeMax and nodeMax == 1:
                            nodeMax = None
                        progressBar = ProgressBar(
                            # -1 for input, -1 for output
                            total_progress_max=processing.totalActiveNodes - g_lastTotalCachedNodes - 2,
                            total_progress_current=finishedNodes - 1,
                            node_progress_max=nodeMax,
                            node_progress_current=nodeValue,
                        )
                        asyncio.run(toYield.put(toPayload(progressBar)))

                if message.get('type') in ('execution_success', 'execution_error', 'execution_interrupted'):
                    asyncio.run(toYield.put(toPayload(None)))

    shared.messages.addMessageReceivedCallback(messageReceivedCallback)

    while True:
        progressBar: str = await toYield.get()
        g_lastProgressBar = progressBar
        yield progressBar


async def progress_sse(request: Request):
    return StreamingResponse(
        content=progressBarUpdates(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


class API:
    def __init__(self, app: FastAPI):
        self.app = app
        self.app.add_api_route(
            "/mcww_api/queue_version",
            queueing.queue.getQueueVersion)
        self.app.add_api_route(
            "/mcww_api/outputs_version/{outputs_key}",
            queueing.queue.getOutputsVersion)
        self.app.add_api_route(
            "/mcww_api/progress_sse",
            progress_sse,
        )

