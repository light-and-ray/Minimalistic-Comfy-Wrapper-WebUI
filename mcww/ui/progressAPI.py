from dataclasses import dataclass, asdict
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
from mcww import queueing, shared
from mcww.utils import saveLogError
import asyncio, json


@dataclass
class ProgressBar:
    total_progress_max: int
    total_progress_current: int
    node_progress_max: int|None
    node_progress_current: int|None

@dataclass
class NodeSegment:
    width_percent: float
    left_percent: float

@dataclass
class ProgressPayload:
    total_progress_percent: float|None
    title_text: str|None
    node_segments: dict[int, NodeSegment]|None


MIN_DUMMY_PERCENT: int = 1


class ProgressAPI:
    def __init__(self, app: FastAPI):
        self.app = app
        self.app.add_api_route(
            "/mcww_api/progress_sse",
            self.progress_sse,
        )
        self.progressToYieldQueues: list[asyncio.Queue] = []
        self.lastProgressBarPayloadStr: str|None = None
        self.nodeSegments: dict[int, NodeSegment] = {}
        shared.messages.addMessageReceivedCallback(self.messageReceivedCallback)


    def progressBarToPayloadStr(self, obj: ProgressBar|None):
        if isinstance(obj, ProgressBar):
            total_max = obj.total_progress_max
            total_current = obj.total_progress_current
            node_max = obj.node_progress_max
            node_current = obj.node_progress_current

            total_progress_percent = None
            total_progress_percent_title = total_current / total_max * 100
            node_progress_percent_title = None

            if node_max is not None:
                if total_current not in self.nodeSegments:
                    self.nodeSegments[total_current] = NodeSegment(
                        width_percent = 100 / total_max,
                        left_percent = 100 / total_max * total_current,
                    )

                node_progress_percent_title = node_current / node_max * 100

                total_max_combined = total_max * node_max
                total_current_combined = total_current * node_max + node_current
                total_progress_percent = (total_current_combined / total_max_combined) * 100
            else:
                total_progress_percent = total_progress_percent_title

            total_progress_percent = max(total_progress_percent, float(MIN_DUMMY_PERCENT))

            title_text = f"[{round(total_progress_percent_title)}%]"
            if len(self.nodeSegments) > 0:
                title_text += f" [{len(self.nodeSegments)}]"
            if node_progress_percent_title:
                title_text += f" [{round(node_progress_percent_title)}%]"

            payload_obj = ProgressPayload(
                total_progress_percent=total_progress_percent,
                node_segments=self.nodeSegments,
                title_text=title_text
            )
            obj = asdict(payload_obj)

        payload = f"data: {json.dumps(obj)}\n\n"
        return payload


    def putToQueues(self, data):
        self.lastProgressBarPayloadStr = data
        for queue in self.progressToYieldQueues:
            asyncio.run(queue.put(data))


    def voidProgressBar(self):
        self.nodeSegments = {}
        self.putToQueues(self.progressBarToPayloadStr(None))


    def dummyProgressBarOnStart(self):
        self.nodeSegments = {}
        self.putToQueues(self.progressBarToPayloadStr(ProgressBar(
            total_progress_max=100, total_progress_current=MIN_DUMMY_PERCENT,
            node_progress_current=None, node_progress_max=None,
        )))


    def messageReceivedCallback(self, message: dict):
        processing = queueing.queue.getInProgressProcessing()
        messagePromptId = message.get('data', {}).get('prompt_id', None)

        if processing and messagePromptId == processing.prompt_id:
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
                    subtractOutputs = 1
                    subtractInputs = 0 if processing.totalCachedNodes else 1
                    # -1 for input, -1 for output
                    total_max = processing.totalActiveNodes - processing.totalCachedNodes - subtractInputs - subtractOutputs
                    total_current = finishedNodes - subtractInputs
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
                    self.putToQueues(self.progressBarToPayloadStr(progressBar))

            if message.get('type') in ('execution_success', 'execution_error', 'execution_interrupted'):
                self.voidProgressBar()
            if message.get('type') == "execution_start":
                processing.totalCachedNodes = 0
                self.dummyProgressBarOnStart()
            if message.get('type') == "execution_cached":
                processing.totalCachedNodes = len(message["data"]["nodes"])
        else:
            if message.get('type') == 'execution_interrupted':
                self.voidProgressBar()


    async def _progressBarSSEHandler(self):
        if isinstance(self.lastProgressBarPayloadStr, str):
            yield self.lastProgressBarPayloadStr

        toYieldQueue = asyncio.Queue()
        self.progressToYieldQueues.append(toYieldQueue)

        try:
            while True:
                progressBar: str = await toYieldQueue.get()
                yield progressBar
        except Exception as e:
            saveLogError(e, "Error on progress bar updates SSE")
        finally: # BaseException child on disconnect
            try:
                self.progressToYieldQueues.remove(toYieldQueue)
            except ValueError:
                pass


    async def progress_sse(self, request: Request):
        return StreamingResponse(
            content=self._progressBarSSEHandler(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )
