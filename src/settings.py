import os, dotenv
import gradio as gr

dotenv.load_dotenv(os.path.join("..", ".env"))
SRC_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
os.chdir(os.path.join(SRC_DIRECTORY, ".."))

COMFY_ADDRESS = os.getenv("COMFY_ADDRESS", "localhost:8188")
COMFY_ADDRESS = COMFY_ADDRESS.lower().removesuffix('/').removeprefix("http://")
CLIENTS_ACCESS_COMFY = os.getenv("CLIENTS_ACCESS_COMFY", "1") != "0"
COMFY_WORKFLOWS_PATH = os.getenv("COMFY_WORKFLOWS_PATH", "")
COMFY_WORKFLOWS_PATH = os.path.realpath(COMFY_WORKFLOWS_PATH)
WEBUI_TITLE = os.getenv("WEBUI_TITLE", "Minimalistic Comfy Wrapper WebUI")

gradio_theme_color = gr.themes.Color(
        '#ffffff',
        '#ffffff',
        '#e3d2f2',
        '#d2c1e0',
        '#c0b0cf',
        '#b0a1be',
        '#9e90ad',
        '#8b7c99',
        '#776a83',
        '#685d71',
        '#5c5364',
        'gray-violet'
    )
GRADIO_THEME = gr.themes.Origin(primary_hue=gradio_theme_color)
