from fastapi import FastAPI
from mcww import queueing

class API:
    def __init__(self, app: FastAPI):
        self.app = app
        self.app.add_api_route(
            "/mcww_api/queue_version",
            queueing.queue.getQueueVersion)
        self.app.add_api_route(
            "/mcww_api/outputs_version/{outputs_key}",
            queueing.queue.getOutputsVersion)

