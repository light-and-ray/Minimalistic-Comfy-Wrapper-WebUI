from dataclasses import dataclass, asdict
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
from mcww import queueing, shared
import asyncio, json


@dataclass
class ProgressBar:
    total_progress_max: int
    total_progress_current: int
    node_progress_max: int | None
    node_progress_current: int | None

@dataclass
class ProgressPayload:
    total_progress_percent: float | None
    node_segment_width_percent: float | None
    node_segment_left_percent: float | None
    title_text: str | None


def progressBarToPayloadStr(obj: ProgressBar | None):
    if isinstance(obj, ProgressBar):
        total_max = obj.total_progress_max
        total_current = obj.total_progress_current
        node_max = obj.node_progress_max
        node_current = obj.node_progress_current

        node_segment_width_percent = None
        node_segment_left_percent = None
        total_progress_percent = None

        total_progress_percent_title = total_current / total_max * 100

        if node_max is not None:
            node_segment_width_percent = 100 / total_max
            node_segment_left_percent = node_segment_width_percent * total_current

            node_progress_percent_title = node_current / node_max * 100
            title_text = f"[{round(total_progress_percent_title)}%] [{round(node_progress_percent_title)}%]"

            total_max_combined = total_max * node_max
            total_current_combined = total_current * node_max + node_current
            total_progress_percent = (total_current_combined / total_max_combined) * 100
        else:
            total_progress_percent = total_progress_percent_title
            title_text = f"[{round(total_progress_percent_title)}%]"

        payload_obj = ProgressPayload(
            total_progress_percent=total_progress_percent,
            node_segment_width_percent=node_segment_width_percent,
            node_segment_left_percent=node_segment_left_percent,
            title_text=title_text
        )
        obj = asdict(payload_obj)

    payload = f"data: {json.dumps(obj)}\n\n"
    return payload


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
            self._progress_sse,
        )
        self.progressToYieldQueues: list[asyncio.Queue] = []
        self.lastTotalCachedNodes = 0
        self.lastProgressBarPayloadStr: str | None = None
        shared.messages.addMessageReceivedCallback(self.messageReceivedCallback)


    def putToQueues(self, data):
        for queue in self.progressToYieldQueues:
            asyncio.run(queue.put(data))


    def messageReceivedCallback(self, message: dict):
        if message.get('type') == 'status':
            self.putToQueues(progressBarToPayloadStr(None))
        if message.get('type') == "execution_start":
            self.lastTotalCachedNodes = 0
        if message.get('type') == "execution_cached":
            self.lastTotalCachedNodes = len(message["data"]["nodes"])

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
                        # -1 for input, -1 for output
                        total_max = processing.totalActiveNodes - self.lastTotalCachedNodes - 2
                        total_current = finishedNodes - 1
                        if nodeMax and nodeMax == 1:
                            nodeMax = None
                        if total_max < 0: total_max = 0
                        total_current = max(0, min(total_current, total_max))
                        progressBar = ProgressBar(
                            total_progress_max=total_max,
                            total_progress_current=total_current,
                            node_progress_max=nodeMax,
                            node_progress_current=nodeValue,
                        )
                        asyncio.run(self.putToQueues(progressBarToPayloadStr(progressBar)))

                if message.get('type') in ('execution_success', 'execution_error', 'execution_interrupted'):
                    asyncio.run(self.putToQueues(progressBarToPayloadStr(None)))


    async def _progressBarUpdates(self):
        if isinstance(self.lastProgressBarPayloadStr, str):
            yield self.lastProgressBarPayloadStr
        toYieldQueue = asyncio.Queue()
        self.progressToYieldQueues.append(toYieldQueue)
        while True:
            progressBar: str = await toYieldQueue.get()
            self.lastProgressBarPayloadStr = progressBar
            yield progressBar


    async def _progress_sse(self, request: Request):
        return StreamingResponse(
            content=self._progressBarUpdates(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

