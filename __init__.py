try:
    import server
    from aiohttp import web

    PORT = 12345

    async def get_my_port_api(request):
        return web.json_response({"port": PORT})

    server.PromptServer.instance.app.add_routes([
        web.get("/my_extension/get_port", get_my_port_api)
    ])

    NODE_CLASS_MAPPINGS = {}

    NODE_DISPLAY_NAME_MAPPINGS = {}

    WEB_DIRECTORY = "./comfy_web_dir"
    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

except ImportError:
    print("The module is not inside comfy context")
