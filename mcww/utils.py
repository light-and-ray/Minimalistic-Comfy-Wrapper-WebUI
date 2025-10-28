import re, os, traceback, logging, random, sys, json
from datetime import datetime
from urllib.parse import urljoin, urlencode, urlparse, parse_qs, urlunparse
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
        print(title_line)
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

def _getComfyPathUrl(path: str, schema: str):
    base_url = f"{schema}://{opts.COMFY_ADDRESS}"
    url = urljoin(base_url, path)
    if opts.COMFY_UI_LOGIN_EXTENSION_TOKEN:
        # Parse the URL to handle existing query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        # Add or update the token parameter
        query_params["token"] = [opts.COMFY_UI_LOGIN_EXTENSION_TOKEN]
        # Reconstruct the URL with the updated query
        updated_query = urlencode(query_params, doseq=True)
        url = urlunparse(parsed_url._replace(query=updated_query))
    return url

def getHttpComfyPathUrl(path: str):
    schema = "https" if opts.COMFY_TLS else "http"
    return _getComfyPathUrl(path, schema)

def getWsComfyPathUrl(path: str):
    schema = "wss" if opts.COMFY_TLS else "ws"
    return _getComfyPathUrl(path, schema)
