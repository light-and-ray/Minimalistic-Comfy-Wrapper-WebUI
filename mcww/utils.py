from typing import Any
import re, os, traceback, logging, random, sys, json, uuid, hashlib
from datetime import datetime
from enum import Enum
from mcww import opts, shared


class DataType(Enum):
    STRING = "string"
    FLOAT = "float"
    INT = "int"
    IMAGE = "image"
    VIDEO = "video"


def save_string_to_file(data: str, filepath: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)


def save_binary_to_file(data, filepath: str) -> None:
    with open(filepath, 'wb') as f:
        f.write(data)


def read_string_from_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def read_binary_from_file(filepath: str):
    with open(filepath, "rb") as f:
        return f.read()


def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split('([0-9]+)', s)
    ]


def applyConsoleFilters():
    class ASGIExceptionFilter(logging.Filter):
        def filter(self, record):
            return "Exception in ASGI application" not in record.getMessage()
    logging.getLogger("uvicorn").addFilter(ASGIExceptionFilter())
    logging.getLogger("uvicorn.error").addFilter(ASGIExceptionFilter())
    logging.getLogger("uvicorn.access").addFilter(ASGIExceptionFilter())
    logging.getLogger("starlette").addFilter(ASGIExceptionFilter())
    logging.getLogger("fastapi").addFilter(ASGIExceptionFilter())
    old_write = sys.stdout.write
    def new_write(s):
        if "To create a public link, set `share=True` in `launch" not in s:
            return old_write(s)
        else:
            sys.stdout.write = old_write
            return old_write("")
    sys.stdout.write = new_write


def initClientID():
    clientID = ""
    clientID += opts.MCWW_DIRECTORY
    clientID += shared.localUrl
    shared.clientID = getStringHash(clientID)


def _getLogFilePath(prefix: str, extension: str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S-%f")
    filepath = os.path.join(opts.STORAGE_DIRECTORY, "log", current_date, f"{prefix}_{current_time}.{extension}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    return filepath


def saveLogError(e, prefixTitleLine:str|None=None, needPrint=True):
    filepath = _getLogFilePath("error", "txt")
    title_line = f"{e.__class__.__name__}: {e}\n\n"
    if prefixTitleLine:
        title_line = prefixTitleLine.strip() + ": " + title_line
    if needPrint:
        print("*** " + title_line)
    stack_trace = traceback.format_exc()
    content = title_line + stack_trace
    save_string_to_file(content, filepath)


def saveLogJson(jsonObj, prefix: str):
    filepath = _getLogFilePath(prefix, "json")
    save_string_to_file(json.dumps(jsonObj, indent=2), filepath)


def generateSeed():
    return random.randrange(start=0, stop=999999999999999)


def isVideoExtension(fileName: str):
    ext = os.path.splitext(fileName)[1].lower().removeprefix('.')
    if ext in ("mp4", "webm"):
        return True
    return False

def isImageExtension(fileName: str):
    ext = os.path.splitext(fileName)[1].lower().removeprefix('.')
    if ext in ("png", "jpeg", "jpg", "webp", "gif", "avif", "heic", "heif", "jxl"):
        return True
    return False

RESTART_TMP_FILE = os.path.normpath(os.path.join(opts.MCWW_DIRECTORY, '..', 'RESTART_REQUESTED'))


def moveValueUp(list_: list, value):
    index = list_.index(value)
    if index == 0:
        return list_
    list_[index-1], list_[index] = list_[index], list_[index-1]
    return list_


def moveKeyUp(dictionary: dict, key):
    keys = list(dictionary.keys())
    keys = moveValueUp(keys, key)
    dictionary = {key : dictionary[key] for key in keys}
    return dictionary


def moveValueDown(list_: list, value):
    index = list_.index(value)
    if index+1 == len(list_):
        return list_
    list_[index+1], list_[index] = list_[index], list_[index+1]
    return list_


def moveKeyDown(dictionary: dict, key):
    keys = list(dictionary.keys())
    keys = moveValueDown(keys, key)
    dictionary = {key : dictionary[key] for key in keys}
    return dictionary


def getFileHash(file: str):
    return hashlib.sha256(read_binary_from_file(file)).hexdigest()

def getStringHash(string: str):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


def getQueueRestoreKey():
    key = ""
    key += getBaseStatesKey()
    key += getFileHash(os.path.join(opts.MCWW_DIRECTORY, 'queueing.py'))
    key += getFileHash(os.path.join(opts.MCWW_DIRECTORY, 'processing.py'))
    key += getFileHash(os.path.join(opts.MCWW_DIRECTORY, 'comfy', 'workflow.py'))
    key = getStringHash(key)
    return key


def getStorageKey():
    key = ""
    key += getBaseStatesKey()
    key += str(opts.FILE_CONFIG.mode)
    key += getFileHash(os.path.join(opts.MCWW_DIRECTORY, 'ui', 'webUIState.py'))
    key = getStringHash(key)
    return key


def getBaseStatesKey():
    file = os.path.join(opts.MCWW_DIRECTORY, '..', 'baseStatesKey')
    if not os.path.exists(file):
        key = str(uuid.uuid4())
        save_string_to_file(key, file)
        print("*** baseStatesKey created")
    else:
        key = read_string_from_file(file)
    return key


def getStorageEncryptionKey():
    file = os.path.join(opts.STORAGE_DIRECTORY, 'browser_storage_encryption_key')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    if not os.path.exists(file):
        key = str(uuid.uuid4())
        save_string_to_file(key, file)
    else:
        key = read_string_from_file(file)
    return key


def getJsStorageKey():
    return getStringHash(f"{getStorageKey()}-{getStorageEncryptionKey()}")


hotkeysReference = """
## Hotkeys Reference
### General

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **R**        | Click Refresh button                                               |
| **Q**        | Open/Close Queue page                                              |
| **H**        | Open/Close Helpers page                                                 |
| **O**        | Open/Close Options page                                                 |
| **P**        | Ensure Project page is open                                 |
| **1 - 9**      | Select tab on Helpers and Options page                             |
| **Ctrl+Enter** | Click Run Button                                                 |
| **Go Back** | Close the sidebar on mobile                                      |
| **Escape** |  Remove focus from active textbox   |
| **Escape** |  Click cancel inside clicked button with confirmation|

### Cursor over a gallery
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **S**        | Click Download button                |
| **F**        | Toggle Fullscreen button      |
| **A**        | Click 🡒A button               |
| **B**        | Click 🡒B button           |
| **C**        | Click A\\|B button               |
| **Space**    | Toggle pause in video               |
| **Ctrl+C**   | Click ⎘ button                         |
| **Ctrl+V**   | Click Paste in image upload area under the cursor         |
| **Go Back**  | Exit fullscreen                                      |
| **Escape**  | Exit fullscreen                                      |
| **E**        | Open in image editor or return to it                |
| **Ctrl+E** or **Shift+E** | Forcefully open in image editor, i.e. don't return to already opened image   |

### Image/Mask editor
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **1 - 9**    | Select tool                             |
| **[/]**  | Change brush size                           |
| **+/-**  | Change opacity                           |
| **C**        | Choose color               |
| **Ctrl+Z**   | Undo                     |
| **Ctrl+Y** or **Ctrl+Shift+Z**   | Redo                     |
| **Ctrl+S**   | Save and go back                               |
| **Go Back**  | Cancel and go back                                    |
| **Go Forward**  | Return to the editor                                   |

### Other pages
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Arrows**   | Select previous/next entry in queue                            |
| **Alt+Arrows** | Move selected queue entry up or down                      |
| **+/-**      | Modify opacity on Compare page/tab                            |
| **S**        | Click Swap button on Compare page/tab                            |
| **Ctrl+S**   | Click Download composite button on Compare page/tab                    |
| **Ctrl+S**   | Click Save button on Presets page                                |
| **A**        | Toggle auto refresh checkbox on Management page                 |
"""


def insensitiveSearch(string: str) -> str:
    string = string.lower()
    string = string.replace('l', '1')
    string = string.replace('i', '1')
    string = string.replace('e', '3')
    string = string.replace('a', '4')
    string = string.replace('s', '5')
    string = string.replace('z', '5')
    string = string.replace('g', '6')
    string = string.replace('t', '7')
    string = string.replace('b', '8')
    string = string.replace('g', '9')
    string = string.replace('o', '0')
    string = string.replace('_', '')
    string = string.replace('-', '')
    string = string.replace(' ', '')
    string = string.replace('~', '')
    string = string.replace('.', '')
    string = string.replace(':', '')
    string = string.replace(';', '')
    return string


def cleanupTerminalOutputs(logs: str):
    lines: Any = logs.split('\n')
    processed_lines = []
    for line in lines:
        if line:
            last_version = line.split('\r')[-1]
            processed_lines.append(last_version)
    result = '\n'.join(processed_lines)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    result = ansi_escape.sub('', result)
    return result


