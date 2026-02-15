import os, dotenv, json
import gradio as gr
import argparse
from dataclasses import dataclass, asdict
from enum import Enum, auto
from mcww.arguments import parseArgs

MCWW_DIRECTORY = os.path.dirname(os.path.normpath(__file__))
dotenv_path = os.path.join(MCWW_DIRECTORY, "..", ".env")
STORAGE_DIRECTORY = os.path.normpath(os.path.join(MCWW_DIRECTORY, '..', "storage/"))

if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

COMFY_ADDRESS = os.getenv("COMFY_ADDRESS", "localhost:8188")
COMFY_ADDRESS = COMFY_ADDRESS.lower().removesuffix('/').removeprefix("http://").removeprefix("https://")
MCWW_WORKFLOWS_SUBDIR = os.getenv("MCWW_WORKFLOWS_SUBDIR", "").strip()
WEBUI_TITLE = os.getenv("WEBUI_TITLE", "Minimalistic Comfy Wrapper WebUI")
WEBUI_TITLE_SHORT = os.getenv("WEBUI_TITLE_SHORT", "MCWW")
COMFY_TLS = os.getenv("COMFY_TLS", "0") == "1"
COMFY_UI_LOGIN_EXTENSION_TOKEN = os.getenv("COMFY_UI_LOGIN_EXTENSION_TOKEN", None)
MCWW_AUTH = os.getenv("MCWW_AUTH", None)
if MCWW_AUTH:
    MCWW_AUTH = json.loads(MCWW_AUTH)
    print("MCWW_AUTH env. variable is loaded")
IS_STANDALONE = True


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


def initializeStandalone():
    global STORAGE_DIRECTORY
    args= parseArgs()
    if args.storage_directory:
        STORAGE_DIRECTORY = args.storage_directory
    os.makedirs(STORAGE_DIRECTORY, exist_ok=True)
    _initialize_file_config(args)
    initializeOptions()


@dataclass
class _Options:
    maxQueueSize: int = 200
    primaryHue: int = 218  # 274 - the old dusty violet
    showToggleDarkLightButton: bool = True
    showRunButtonCopy: bool = False
    openAccordionsAutomatically: bool = False
    autoRefreshPageOnBackendRestarted: bool = False
    hideSidebarByDefault: bool = False
    defaultVideosVolume: float = 1.0
    mirrorWebCamera: bool = True
    hiddenWorkflows: list[str] = None
    def __init__(self):
        self.hiddenWorkflows = []
    forceShowBatchCount: bool = False

options: _Options = None


def initializeOptions():
    global options
    from mcww.utils import read_string_from_file, saveLogError
    path = os.path.join(STORAGE_DIRECTORY, "options.json")
    options = _Options()
    if os.path.exists(path):
        try:
            loaded = json.loads(read_string_from_file(path))
            optionsDict = asdict(options)
            for key in optionsDict.keys():
                try:
                    if key in loaded:
                        setattr(options, key, loaded[key])
                except Exception as e:
                    saveLogError(e, f"Error on loading option '{key}'")
        except Exception as e:
            saveLogError(e, "Error on loading options from file")


def saveOptions():
    global options
    from mcww.utils import save_string_to_file
    path = os.path.join(STORAGE_DIRECTORY, "options.json")
    save_string_to_file(json.dumps(asdict(options), indent=2), path)


def getThemeColor(hue):
    return gr.themes.Color(
        c50=f'hsl({hue}, 85%, 100%)',
        c100=f'hsl({hue}, 85%, 95%)',
        c200=f'hsl({hue}, 55%, 89%)',
        c300=f'hsl({hue}, 33%, 82%)',
        c400=f'hsl({hue}, 24%, 75%)',
        c500=f'hsl({hue}, 18%, 69%)',
        c600=f'hsl({hue}, 18%, 61%)',
        c700=f'hsl({hue}, 14%, 53%)',
        c800=f'hsl({hue}, 14%, 43%)',
        c900=f'hsl({hue}, 13%, 39%)',
        c950=f'hsl({hue}, 13%, 34%)',
        name=f'dusty-{hue}'
    )


def getTheme():
    primary_hue = getThemeColor(options.primaryHue)
    secondary_hue = gr.themes.colors.blue
    neutral_hue = gr.themes.colors.zinc
    font = [
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
    ]
    themeClass = gr.themes.Origin
    return themeClass(primary_hue=primary_hue, secondary_hue=secondary_hue,
                                    neutral_hue=neutral_hue, font=font)
