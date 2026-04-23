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


def getThemeColor(hue: int, saturationList: str, lightnessList: str):
    saturationList = json.loads(saturationList)
    lightnessList = json.loads(lightnessList)
    params = ["c50", "c100", "c200", "c300", "c400", "c500", "c600", "c700", "c800", "c900", "c950"]
    kwargs = {}
    for param, saturation, lightness in zip(params, saturationList, lightnessList):
        kwargs[param] = f'hsl({hue}, {saturation}%, {lightness}%)'
    return gr.themes.Color(**kwargs)


def getTheme():
    primary_hue = getThemeColor(options.primaryHue,
        options.primarySaturationList, options.primaryLightnessList)
    secondary_hue = SECONDARY_COLORS[options.secondaryColor]
    neutral_hue = NEUTRAL_COLORS[options.neutralColor]
    font = [
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
    ]
    themeClass = THEME_CLASSES[options.themeClass]
    return themeClass(primary_hue=primary_hue, secondary_hue=secondary_hue,
                                    neutral_hue=neutral_hue, font=font)


HUE_PRESETS = {
    "Fire": 7,
    "Burnt": 13,
    "Mandarin": 25,
    "Orange": 30,
    "Gold": 41,
    "Yellow": 51,
    "Lettuce": 70,
    "Lime": 91,
    "Green": 111,
    "Mint": 145,
    "Aqua": 169,
    "Cyan": 178,
    "Sky": 200,
    "Cobalt": 218,
    "Blue": 229,
    "Indigo": 239,
    "Iris": 260,
    "Violet": 274,
    "Purple": 288,
    "Magenta": 300,
    "Fuchsia": 326,
    "Raspberry": 343,
    "Crimson": 352,
    "Red": 360,
}

SL_PRESETS = {
    "Dusty": ['[85, 85, 55, 33, 24, 18, 18, 14, 14, 13, 13]', '[100, 95, 89, 82, 75, 69, 61, 53, 43, 39, 34]'],
    "Pastel": ['[85, 85, 80, 75, 73, 69, 65, 60, 60, 55, 50]', '[98, 95, 92, 88, 84, 78, 75, 72, 68, 65, 60]'],
    "Light": ['[100, 100, 96, 94, 89, 84, 75, 58, 55, 47, 37]', '[97, 94, 89, 82, 74, 67, 59, 51, 41, 34, 27]'],
    "Normal": ['[100, 94, 94, 95, 93, 89, 98, 96, 90, 80, 80]', '[97, 94, 86, 74, 60, 48, 39, 32, 27, 24, 22]'],
    "Bright": ['[100, 95, 97, 96, 94, 91, 83, 76, 71, 64, 54]', '[97, 93, 87, 78, 68, 60, 53, 48, 40, 33, 25]'],
    "Vibrant": ['[100, 100, 100, 97, 96, 95, 90, 88, 79, 75, 71]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
    "Pale": ['[65, 55, 39, 38, 36, 38, 40, 43, 44, 44, 50]', '[97, 93, 88, 80, 63, 55, 50, 45, 40, 36, 33]'],
    "Dark": ['[65, 55, 39, 38, 36, 38, 40, 43, 44, 44, 50]', '[92, 85, 77, 62, 53, 45, 38, 32, 25, 20, 13]'],
    "White": ['[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]', '[100, 97, 95, 91, 84, 80, 77, 75, 70, 68, 65]'],
    "Gray": ['[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
    "Black": ['[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]', '[88, 80, 72, 62, 51, 40, 30, 20, 13, 10, 8]'],
}

FEATURED_COLORS = {
    "Default": [HUE_PRESETS["Cobalt"], *SL_PRESETS["Dusty"]],
    "MCWW Classic": [HUE_PRESETS["Violet"], *SL_PRESETS["Dusty"]],
    "Dusty Yellow": [HUE_PRESETS["Yellow"], *SL_PRESETS["Dusty"]],
    "Perfect Pink": [HUE_PRESETS["Fuchsia"], *SL_PRESETS["Pastel"]],
    "Error Red": [HUE_PRESETS["Red"], *SL_PRESETS["Vibrant"]],
    "Gradio Orange": [HUE_PRESETS["Mandarin"], *SL_PRESETS["Vibrant"]],
    "Gradio Indigo": [HUE_PRESETS["Indigo"], *SL_PRESETS["Light"]],
    "Gradio Sky": [HUE_PRESETS["Sky"], *SL_PRESETS["Normal"]],
}

def RoundedTheme(*args, **kwargs):
    theme = gr.themes.Ocean(*args, **kwargs)
    # remove gradient from secondary to primary
    attributes = ['button_primary_background_fill', 'button_primary_background_fill_dark',
        'button_primary_background_fill_hover', 'button_primary_background_fill_hover_dark']
    for attribute in attributes:
        value = getattr(theme, attribute)
        value = value.replace('secondary', 'primary')
        setattr(theme, attribute, value)
    return theme

def SharpTheme(*args, **kwargs):
    theme = gr.themes.Monochrome(*args, **kwargs)
    reference = gr.themes.Origin()
    # add colors
    attributes = ['button_primary_background_fill', 'button_primary_background_fill_dark',
        'button_primary_background_fill_hover', 'button_primary_background_fill_hover_dark',
        'slider_color', 'slider_color_dark']
    for attribute in attributes:
        value = getattr(theme, attribute)
        value = value.replace('neutral', 'primary')
        setattr(theme, attribute, value)
    attributes = ['button_cancel_background_fill', 'button_cancel_background_fill_hover',
        'button_cancel_background_fill_dark', 'button_cancel_background_fill_dark',
        'button_cancel_background_fill_hover_dark', 'button_cancel_border_color',
        'button_cancel_border_color_dark', 'button_cancel_border_color_hover',
        'button_cancel_border_color_hover_dark']
    for attribute in attributes:
        value = getattr(reference, attribute)
        setattr(theme, attribute, value)
    # fix light theme ugliness
    theme.button_secondary_border_color = "*neutral_200"
    theme.button_primary_border_color = "*primary_300"
    theme.button_primary_background_fill = "*primary_200"
    theme.button_primary_background_fill_hover = "*primary_200"
    theme.button_primary_text_color = "*primary_700"
    theme.button_primary_text_color_hover = "*primary_700"
    theme.button_secondary_text_color_hover = theme.button_secondary_text_color
    theme.slider_color = "*primary_400"
    # fix dark theme ugliness
    theme.button_secondary_border_color_dark = "*neutral_800"
    theme.button_secondary_border_color_hover_dark = "*neutral_700"
    theme.input_background_fill_dark = "*neutral_800"
    theme.input_border_color_dark = "*neutral_700"
    theme.input_border_width_dark = "1px"
    theme.background_fill_primary_dark = reference.background_fill_primary_dark
    return theme

grayDarker = getThemeColor(hue=240, saturationList='[0, 5, 6, 5, 5, 4, 5, 5, 4, 6, 6]',
        lightnessList='[98, 96, 90, 84, 75, 46, 34, 20, 12, 10, 5]')

THEME_CLASSES = {
    "Origin": gr.themes.Origin,
    "Flat": gr.themes.Default,
    "Soft": gr.themes.Soft,
    "Rounded": RoundedTheme,
    "Sharp": SharpTheme,
}

SECONDARY_COLORS = {
    "blue": gr.themes.colors.blue,
    "indigo": gr.themes.colors.indigo,
}

NEUTRAL_COLORS = {
    "gray_darker": grayDarker,
    "zinc_blue": gr.themes.colors.gray, # zinc is a bluish color. In gradio zinc and gray are mixed up
    "slate_blue": gr.themes.colors.slate,
    "gray_yellowish": gr.themes.colors.neutral,
    "stone_yellow": gr.themes.colors.stone,
    "gray_original": gr.themes.colors.zinc, # this isn't bluish
}

MCWW_THEME_FLAGS = ["Bold", "Borderless", "Rounded"]

FEATURED_THEMES = {
    "Default": ["Origin", "blue", "gray_darker", []],
    "MCWW Flat": ["Flat", "blue", "gray_darker", []],
    "MCWW Rounded": ["Rounded", "blue", "gray_darker", ["Bold", "Rounded"]],
    "MCWW Float": ["Soft", "blue", "gray_darker", ["Bold", "Borderless"]],
    "MCWW Sharp": ["Sharp", "blue", "gray_darker", ["Bold"]],
    "Gradio Classic": ["Origin", "blue", "zinc_blue", []],
    "Gradio Soft": ["Soft", "indigo", "zinc_blue", ["Bold", "Borderless"]],
    "Wan2GP": ["Soft", "indigo", "slate_blue", ["Bold", "Borderless"]],
}

FEATURED_THEMES_COLORS = {
    "Gradio Classic": FEATURED_COLORS["Gradio Orange"],
    "Gradio Soft": FEATURED_COLORS["Gradio Indigo"],
    "Wan2GP": FEATURED_COLORS["Gradio Sky"],
}

@dataclass
class _Options:
    maxQueueSize: int = 200
    primaryHue: int = FEATURED_COLORS["Default"][0]
    primarySaturationList: str = FEATURED_COLORS["Default"][1]
    primaryLightnessList: str = FEATURED_COLORS["Default"][2]
    themeClass: str = FEATURED_THEMES["Default"][0]
    secondaryColor: str = FEATURED_THEMES["Default"][1]
    neutralColor: str = FEATURED_THEMES["Default"][2]
    themeFlags: list[str] = None
    preferredThemeDarkLight: str = "System"
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
    presetsFilterThreshold: int = 30
    useCustomContextMenu: bool = True
    maxClipboardHistoryLength: int = 20
    restartComfyIfTooLittleGBOfRamIsAvailable: float = 0.0
    titleInMediaSession: bool = False
    noteLengthCollapseLimit: int = 300
    overflowGalleryGroupSize: int = 50
    protectUrlsInMarkdownOutput: bool = True

    def __init__(self):
        self.hiddenWorkflows = []
        self.themeFlags = FEATURED_THEMES["Default"][3]

    def ensureNoConflicts(self):
        if self.defaultPriority > self.queueMaxPriority:
            self.defaultPriority = 1
        try:
            getThemeColor(self.primaryHue,
                self.primarySaturationList, self.primaryLightnessList)
        except Exception as e:
            print(f"*** Error on validating primary theme options: {e.__class__.__name__}: {e}")
            print("*** Using Vibrant Red")
            self.primaryHue = FEATURED_COLORS["Error Red"][0]
            self.primarySaturationList = FEATURED_COLORS["Error Red"][1]
            self.primaryLightnessList = FEATURED_COLORS["Error Red"][2]
        try:
            getTheme()
        except Exception as e:
            print(f"*** Error on validating theme: {e.__class__.__name__}: {e}")
            print("*** Using Default")
            self.themeClass: str = FEATURED_THEMES["Default"][0]
            self.secondaryColor: str = FEATURED_THEMES["Default"][1]
            self.neutralColor: str = FEATURED_THEMES["Default"][2]

        if self.preferredThemeDarkLight not in ["System", "Dark", "Light"]:
            self.preferredThemeDarkLight = "System"


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

