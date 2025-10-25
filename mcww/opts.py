import os, dotenv, json
import gradio as gr
import argparse
from dataclasses import dataclass
from enum import Enum, auto
from mcww.arguments import parseArgs

MCWW_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(MCWW_DIRECTORY, "..", ".env")
STORAGE_DIRECTORY = os.path.normpath(os.path.join(MCWW_DIRECTORY, '..', "storage/"))

if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

COMFY_ADDRESS = os.getenv("COMFY_ADDRESS", "localhost:8188")
COMFY_ADDRESS = COMFY_ADDRESS.lower().removesuffix('/').removeprefix("http://")
COMFY_WORKFLOWS_PATH = ""
WEBUI_TITLE = os.getenv("WEBUI_TITLE", "Minimalistic Comfy Wrapper WebUI")
COMFY_TLS = os.getenv("COMFY_TLS", "0") == "1"
COMFY_UI_LOGIN_EXTENSION_TOKEN = os.getenv("COMFY_UI_LOGIN_EXTENSION_TOKEN", None)
MCWW_AUTH = os.getenv("MCWW_AUTH", None)
if MCWW_AUTH:
    MCWW_AUTH = json.loads(MCWW_AUTH)
    print("MCWW_AUTH env. variable is loaded")


dullViolet = gr.themes.Color(
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
        'dull-violet'
    )
primary_hue = dullViolet
secondary_hue = gr.themes.colors.blue
neutral_hue = gr.themes.colors.zinc
themeClass = gr.themes.Origin
GRADIO_THEME = themeClass(primary_hue=primary_hue, secondary_hue=secondary_hue,
                                                neutral_hue=neutral_hue)


class FilesMode(Enum):
    SAME_SERVER = auto()
    MIRROR = auto()
    DIRECT_LINKS = auto()


@dataclass(frozen=True)
class _FileConfig:
    mode: FilesMode
    input_dir: str = None
    output_dir: str = None

FILE_CONFIG: _FileConfig = None


def _initialize_file_config(args: argparse.Namespace) -> None:
    """
    Initializes the global file_config variable based on parsed arguments.
    Raises an error if required arguments for a mode are missing.
    """
    global FILE_CONFIG

    mode = getattr(FilesMode, args.files_mode.upper())
    input_dir = None
    output_dir = None

    if mode == FilesMode.SAME_SERVER:
        base_dir = args.comfy_base_directory

        output_dir = args.comfy_output_directory
        input_dir = args.comfy_input_directory

        if not (base_dir or output_dir and input_dir and args.workflows_path):
            print(
                "The argument --comfy-base-directory or {--comfy-output-directory, "
                "--comfy-input-directory, --workflows-path} is required when "
                "--files-mode is set to 'same_server'. See .env.example "
                "or Readme.md for details"
            )
            exit(1)

        if not output_dir:
            output_dir = os.path.join(base_dir, "output")

        if not input_dir:
            input_dir = os.path.join(base_dir, "input")

    elif mode == FilesMode.MIRROR:
        # The paths are relative to the mirror storage directory
        input_dir = os.path.join(STORAGE_DIRECTORY, "input")
        output_dir = os.path.join(STORAGE_DIRECTORY, "output")

    # Direct links mode has no paths, so input_dir and output_dir remain None

    FILE_CONFIG = _FileConfig(mode=mode, input_dir=input_dir, output_dir=output_dir)


def _initialize_workflow_path(args):
    global COMFY_WORKFLOWS_PATH
    if args.workflows_path:
        COMFY_WORKFLOWS_PATH = args.workflows_path
    else:
        if FILE_CONFIG.mode == FilesMode.SAME_SERVER:
            COMFY_WORKFLOWS_PATH = os.path.join(
                    args.comfy_base_directory,
                    "user",
                    "default",
                    "workflows"
                )
        else:
            COMFY_WORKFLOWS_PATH = "workflows"

        print(f"Workflows path is automatically set to '{os.path.abspath(COMFY_WORKFLOWS_PATH)}'. "
                        "Use --workflows-path to override it")


def initializeStandalone():
    global STORAGE_DIRECTORY
    args= parseArgs()
    if args.storage_directory:
        STORAGE_DIRECTORY = args.storage_directory
    _initialize_file_config(args)
    _initialize_workflow_path(args)


showNamesInGallery = False

easterEggWolf3dIframe = f'''
<iframe
    src="{os.getenv("WOLF_3D_URL", "https://git.nihilogic.dk/wolf3d/")}"
    width="640"
    height="480"
    frameborder="0"
    allowfullscreen
></iframe>
'''
