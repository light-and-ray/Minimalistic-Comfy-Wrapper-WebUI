import re, os, traceback, logging, random, sys, json
from datetime import datetime
from enum import Enum
from mcww import opts


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
    return random.randrange(start=-999999999999999, stop=999999999999999)


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


def getGitCommit():
    try:
        gitDir = os.path.join(opts.MCWW_DIRECTORY, '..', '.git')
        if not os.path.exists(gitDir):
            print(".git directory not found")
            return None
        head = read_string_from_file(os.path.join(gitDir, 'HEAD')).strip()
        if head.startswith('ref: '):
            args = head.removeprefix('ref: ').split('/')
            headPath = os.path.join(gitDir, *args)
            head = read_string_from_file(headPath).strip()
        return head
    except Exception as e:
        saveLogError(e, "Unexpected error while parsing git commit")
        return None

def getStorageKey():
    key = f"{getGitCommit()}/{str(opts.FILE_CONFIG.mode)}"
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


hotkeysReference = """
## Hotkeys Reference

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **R**        | Click Refresh button                                               |
| **Q**        | Click Queue button                                                 |
| **Enter**    | Click Run Button                                           |
| **S**        | Click Download button in gallery under the cursor                |
| **F**        | Toggle Fullscreen in gallery under the cursor     |
| **A**        | Click 🡒A button in gallery under the cursor               |
| **B**        | Click 🡒B button in gallery under the cursor          |
| **C**        | Click A\\|B button in gallery under the cursor              |
| **Ctrl+C**   | Click ⎘ button in gallery under the cursor                                                                  |
| **Ctrl+V**   | Click Paste in image upload area under the cursor         |
| **ArrowUp**  | Select previous entry in queue                            |
| **ArrowDown**| Select next entry in queue                                  |
"""

