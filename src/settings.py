import os

COMFY_ADDRESS = os.getenv("COMFY_ADDRESS", "localhost:8188")
COMFY_ADDRESS = COMFY_ADDRESS.lower().removesuffix('/').removeprefix("http://")
COMFY_WORKFLOWS_PATH = os.getenv("COMFY_WORKFLOWS_PATH", "")
COMFY_WORKFLOWS_PATH = os.path.join("..", COMFY_WORKFLOWS_PATH)
COMFY_WORKFLOWS_PATH = os.path.realpath(COMFY_WORKFLOWS_PATH)
