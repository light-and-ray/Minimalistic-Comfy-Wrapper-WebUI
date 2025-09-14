import os, dotenv
import gradio as gr
import argparse
from dataclasses import dataclass
from enum import Enum, auto
from arguments import parseArgs

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

        # Check if --comfy-base-directory is provided
        if not base_dir:
            raise argparse.ArgumentError(
                None,
                "The argument --comfy-base-directory is required when --files-mode is set to 'same_server'."
            )

        output_dir = args.comfy_output_directory
        input_dir = args.comfy_input_directory

        # Use the base directory if specific directories are not provided
        if not output_dir:
            output_dir = os.path.join(base_dir, "output")

        if not input_dir:
            input_dir = os.path.join(base_dir, "input")

    elif mode == FilesMode.MIRROR:
        storage_dir = args.mirror_storage_directory
        # The paths are relative to the mirror storage directory
        input_dir = os.path.join(storage_dir, "input")
        output_dir = os.path.join(storage_dir, "output")

    # Direct links mode has no paths, so input_dir and output_dir remain None

    FILE_CONFIG = _FileConfig(mode=mode, input_dir=input_dir, output_dir=output_dir)


def initialize():
    args= parseArgs()
    _initialize_file_config(args)


SUPPRESS_NODE_SKIPPING_WARNING: set[str] = set(["MarkdownNote"])
