from ntpath import dirname
from typing import Never
import re, os, traceback, logging, random
import uuid, sys, json
from datetime import datetime
from mcww import opts
from urllib.parse import urljoin, urlencode, urlparse, parse_qs, urlunparse
import gradio as gr
from enum import Enum


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


MCWW_WEB_DIR = os.path.normpath(os.path.join(opts.MCWW_DIRECTORY, '..', 'mcww_web'))

def _concat_files(directory):
    # Process JS files (script.js first)
    js_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                if file == 'script.js':
                    js_files.insert(0, os.path.join(root, file))  # Ensure script.js is first
                else:
                    js_files.append(os.path.join(root, file))

    ifaceJS = "\n".join(read_string_from_file(f) for f in js_files)

    # Process CSS files
    css_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.css'):
                css_files.append(os.path.join(root, file))

    ifaceCSS = "\n".join(read_string_from_file(f) for f in css_files)

    return ifaceJS, ifaceCSS

ifaceJS, ifaceCSS = _concat_files(MCWW_WEB_DIR)
def getIfaceCustomHead():
    schema = "https" if opts.COMFY_TLS else "http"
    frontendComfyLink = f'"{schema}://{opts.COMFY_ADDRESS}"'
    try:
        if ':' in opts.COMFY_ADDRESS and len(opts.COMFY_ADDRESS.split(':')) == 2:
            comfyHost, comfyPort = opts.COMFY_ADDRESS.split(':')
            if comfyHost in ["0.0.0.0", "127.0.0.1", "localhost"]:
                frontendComfyLink = f"buildLocalLink({comfyPort})"
    except Exception as e:
        print(f"*** Unexpected error while preparing comfy frontend link: {e.__class__.__name__}: {e}")
    ifaceCustomHead = (
        "<script>"
            f"const COMFY_ADDRESS = {frontendComfyLink};\n\n"
            f"{ifaceJS}\n\n"
        "</script>"
    )
    return ifaceCustomHead
logoPath = os.path.join(MCWW_WEB_DIR, 'logo.svg')
logoHtml = read_string_from_file(logoPath)


def raiseGradioError(e: Exception, silent=False) -> Never:
    text = f"{e.__class__.__name__}: {e}"
    if not silent:
        print(traceback.format_exc())
    raise gr.Error(text[:100], print_exception=False)


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
        print(f"*** Unexpected error while parsing git commit: {e.__class__.__name__}: {e}")
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


def getMcwwLoaderHTML(classes):
    offset = random.uniform(0.1, 0.25)
    frameA = random.uniform(0.0, 0.6)
    frameB = frameA + offset
    frameC = frameB + offset
    return f'''
    <div class="mcww-loader-container {' '.join(classes)}">
        <div class="mcww-wobble-circles">
            <div class="mcww-circle" style="animation-delay: -{frameA}s;"></div>
            <div class="mcww-circle" style="animation-delay: -{frameB}s;"></div>
            <div class="mcww-circle" style="animation-delay: -{frameC}s;"></div>
        </div>
        <div class="mcww-loader-text">Loading...</div>
    </div>
'''

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


def getRunJSFunctionKwargs(dummyComponent):
    def runJSFunctionKwargs(jsFunctions) -> dict:
        if isinstance(jsFunctions, str):
            jsFunctions = [jsFunctions]
        jsCode = '(async function (...args) {'
        for jsFunction in jsFunctions:
            jsCode += f"await {jsFunction}();"
        jsCode += '})'
        return dict(
                fn=lambda x: x,
                inputs=[dummyComponent],
                outputs=[dummyComponent],
                js=jsCode,
        )
    return runJSFunctionKwargs

def _getLogFilePath(prefix: str, extension: str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S-%f")
    filepath = os.path.join(opts.STORAGE_DIRECTORY, "log", current_date, f"{prefix}_{current_time}.{extension}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    return filepath


def showRenderingErrorGradio(e):
    gr.Markdown(f"Critical error on rendering, report it on github\n\n"
                    f"{e.__class__.__name__}: {e}\n\n"
                    f"```\n{traceback.format_exc()}\n```\n",
            elem_classes=["mcww-visible"])


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
