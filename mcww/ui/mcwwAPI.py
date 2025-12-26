from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import Response
from mcww import queueing
from mcww.ui.uiUtils import pwaIconBytes
from mcww.ui.progressAPI import ProgressAPI

PWA_MANIFEST = \
{
    "name": "Minimalistic Comfy Wrapper WebUI",
    "icons": [
        {
            "src": "/pwa_icon.png",
            "sizes": "1024x1024",
            "type": "image/png",
            "purpose": "maskable",
        },
        {
            "src": "/pwa_icon.png",
            "sizes": "1024x1024",
            "type": "image/png",
        }
    ],
    "start_url": "./",
    "display": "standalone"
}


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
        self.removeRoute('/pwa_icon')
        self.app.add_api_route(
            '/pwa_icon.png',
            lambda: Response(content=pwaIconBytes, media_type="image/png"),
            methods=["GET"],
            name="pwa_icon",
        )
        self.removeRoute('/manifest.json')
        self.app.add_api_route(
            '/manifest.json',
            lambda: PWA_MANIFEST,
            methods=["GET"]
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


    def removeRoute(self, path: str):
        self.app.routes[:] = [
            route for route in self.app.routes
            if not (isinstance(route, APIRoute) and route.path == path)
        ]
