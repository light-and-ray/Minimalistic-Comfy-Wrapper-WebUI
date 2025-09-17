try:
    import server
except ImportError:
    print("The module is not inside comfy context")
else:
    from aiohttp import web
    import os, sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from mcww import comfyExtension

    async def get_my_port_api(request):
        return web.json_response({"port": comfyExtension.getPort()})

    server.PromptServer.instance.app.add_routes([
        web.get("/my_extension/get_port", get_my_port_api)
    ])

    comfyExtension.launchInThread()

    NODE_CLASS_MAPPINGS = {}

    NODE_DISPLAY_NAME_MAPPINGS = {}

    WEB_DIRECTORY = "./comfy_web_dir"
    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
