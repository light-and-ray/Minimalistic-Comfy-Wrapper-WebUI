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


HUE_PRESETS = {
    "Orange": 25,
    "Yellow": 54,
    "Green": 100,
    "Mint": 145,
    "Turquoise": 169,
    "Cyan": 181,
    "Blue": 218,
    "Violet": 274,
    "Purple": 288,
    "Magenta": 326,
    "Red": 360,
}

SL_PRESETS = {
    "Dusty": ['[85, 85, 55, 33, 24, 18, 18, 14, 14, 13, 13]', '[100, 95, 89, 82, 75, 69, 61, 53, 43, 39, 34]'],
    "Pastel": ['[85, 85, 80, 75, 73, 69, 65, 60, 60, 55, 50]', '[91, 88, 85, 82, 80, 78, 75, 72, 68, 65, 60]'],
    "Normal": ['[100, 95, 97, 96, 94, 91, 83, 76, 71, 64, 54]', '[97, 93, 87, 78, 68, 60, 53, 48, 40, 33, 25]'],
    "Vibrant": ['[100, 100, 100, 97, 96, 95, 90, 88, 79, 75, 71]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
    "Pale": ['[65, 55, 39, 38, 36, 38, 40, 43, 44, 44, 50]', '[92, 85, 77, 72, 63, 55, 50, 45, 40, 36, 33]'],
    "Dark": ['[65, 55, 39, 38, 36, 38, 40, 43, 44, 44, 50]', '[92, 85, 77, 62, 53, 45, 38, 32, 25, 20, 13]'],
    "Gray L": ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[95, 90, 88, 85, 83, 80, 77, 75, 70, 68, 65]'],
    "Gray N": ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
    "Gray D": ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[88, 80, 72, 62, 51, 40, 30, 20, 13, 10, 8]'],
}

DEFAULT_PRIMARY_SATURATION_LIST, DEFAULT_PRIMARY_LUMINANCE_LIST = SL_PRESETS["Dusty"]
DEFAULT_HUE = HUE_PRESETS["Blue"]


@dataclass
class _Options:
    maxQueueSize: int = 200
    primaryHue: int = DEFAULT_HUE
    primarySaturationList: str = DEFAULT_PRIMARY_SATURATION_LIST
    primaryLuminanceList: str = DEFAULT_PRIMARY_LUMINANCE_LIST
    showToggleDarkLightButton: bool = True
    showRunButtonCopy: bool = False
    openAccordionsAutomatically: bool = False
    autoRefreshPageOnBackendRestarted: bool = False
    hideSidebarByDefault: bool = False
    defaultVideosVolume: float = 1.0
    mirrorWebCamera: bool = True
    hiddenWorkflows: list[str] = None
    forceShowBatchCount: bool = False
    hideHomepagesInFooter: bool = False
    queueMaxPriority: int = 3
    defaultPriority: int = 1

    def __init__(self):
        self.hiddenWorkflows = []

    def ensureNoConflicts(self):
        if self.defaultPriority > self.queueMaxPriority:
            self.defaultPriority = 1
        try:
            getThemeColor(self.primaryHue,
                self.primarySaturationList, self.primaryLuminanceList)
        except Exception as e:
            print(f"*** Error on validating primary theme options: {e.__class__.__name__}: {e}")
            print("*** Using Vibrant Red")
            self.primaryHue = HUE_PRESETS["Red"]
            self.primarySaturationList, self.primaryLuminanceList = SL_PRESETS["Vibrant"]

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
            options.ensureNoConflicts()
        except Exception as e:
            saveLogError(e, "Error on loading options from file")


def saveOptions():
    global options
    options.ensureNoConflicts()
    from mcww.utils import save_string_to_file
    path = os.path.join(STORAGE_DIRECTORY, "options.json")
    save_string_to_file(json.dumps(asdict(options), indent=2), path)


def getThemeColor(hue: int, saturationList: str, luminanceList: str):
    saturationList = json.loads(saturationList)
    luminanceList = json.loads(luminanceList)
    params = ["c50", "c100", "c200", "c300", "c400", "c500", "c600", "c700", "c800", "c900", "c950"]
    kwargs = {}
    for param, saturation, luminance in zip(params, saturationList, luminanceList):
        kwargs[param] = f'hsl({hue}, {saturation}%, {luminance}%)'
    return gr.themes.Color(**kwargs)


def getTheme():
    primary_hue = getThemeColor(options.primaryHue,
        options.primarySaturationList, options.primaryLuminanceList)
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
