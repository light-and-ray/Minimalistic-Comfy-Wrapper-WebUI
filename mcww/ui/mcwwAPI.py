from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse
from mcww import queueing
from mcww.ui.uiUtils import logoWithBGHtml
from mcww.ui.progressAPI import ProgressAPI


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
            "/mcww_api/queue_indicator",
            self.getQueueIndicatorEndpoint)
        app.routes[:] = [
            route for route in app.routes
            if not (isinstance(route, APIRoute) and route.path == '/pwa_icon')
        ]
        self.app.add_api_route(
            '/pwa_icon',
            lambda: HTMLResponse(content=logoWithBGHtml),
            methods=["GET"],
            name="pwa_icon",
        )
        self.progressAPI = ProgressAPI(self.app)
        self.lastQueueVersion = None
        self.lastQueueIndicator = None


    def getQueueIndicatorEndpoint(self):
        version = queueing.queue.getQueueVersion()
        if self.lastQueueVersion == version:
            return self.lastQueueIndicator
        else:
            self.lastQueueVersion = version
            self.lastQueueIndicator = queueing.queue.getQueueIndicator()
            return self.lastQueueIndicator

