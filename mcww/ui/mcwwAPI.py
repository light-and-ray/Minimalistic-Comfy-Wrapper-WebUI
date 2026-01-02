import os
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import Response
from mcww import queueing, opts
from mcww.utils import read_binary_from_file
from mcww.ui.uiUtils import MCWW_WEB_DIR
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
        self.lastQueueVersion = None
        self.lastQueueIndicator = None
        self.progressAPI = ProgressAPI(self.app)
        self.setUpPWA()


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


    def _addFileRoute(self, path: str):
        filePath = os.path.join(MCWW_WEB_DIR, *path.split('/'))
        fileBytes = read_binary_from_file(filePath)
        media_type = ""
        headers = {}
        if path.endswith('.png'):
            media_type = "image/png"
        elif path.endswith('.js'):
            media_type = "application/javascript"
            headers["Service-Worker-Allowed"] = "/"
        elif path.endswith('.html'):
            media_type = "text/html"
        self.app.add_api_route(
            path,
            lambda: Response(
                content=fileBytes,
                media_type=media_type,
                headers=headers
            ),
            methods=["GET"],
        )


    def setUpPWA(self):
        self.removeRoute('/pwa_icon')
        self._addFileRoute('/pwa/icon.png')
        self._addFileRoute('/pwa/serviceWorker.js')

        manifest =  {
            "name": opts.WEBUI_TITLE,
            "icons": [
                {
                    "src": '/pwa/icon.png',
                    "sizes": "1024x1024",
                    "type": "image/png",
                    "purpose": "maskable",
                },
                {
                    "src": '/pwa/icon.png',
                    "sizes": "1024x1024",
                    "type": "image/png",
                }
            ],
            "start_url": "./",
            "display": "standalone"
        }

        self.removeRoute('/manifest.json')
        self.app.add_api_route(
            '/manifest.json',
            lambda: manifest,
            methods=["GET"]
        )

