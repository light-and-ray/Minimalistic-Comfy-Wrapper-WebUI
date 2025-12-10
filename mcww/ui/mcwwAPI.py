from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request
from mcww import queueing
import asyncio, json


async def generate_progress_updates():
    total_progress_max = 10
    total_progress_current = 0
    node_progress_max = None
    node_progress_current = None
    async def send():
        # Yield SSE event
        data = {
            "total_progress_max": total_progress_max,
            "total_progress_current": total_progress_current,
            "node_progress_max": node_progress_max,
            "node_progress_current": node_progress_current
        }
        await asyncio.sleep(1)
        return f"data: {json.dumps(data)}\n\n"


    while total_progress_current < total_progress_max:
        total_progress_current += 1
        if total_progress_current == 4:
            node_progress_max = 6
        else:
            node_progress_max = None
        if node_progress_max:
            for node_progress_current in range(0, node_progress_max):
                yield await send()
        else:
            yield await send()


async def progress_sse(request: Request):
    return StreamingResponse(
        generate_progress_updates(),
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

