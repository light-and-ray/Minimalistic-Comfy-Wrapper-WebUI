from typing import Never
import re, os, hashlib, traceback, logging, random
import uuid
from mcww import opts
from PIL import Image
import gradio as gr

def save_string_to_file(data: str, filepath: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)


def save_binary_to_file(data, filepath: str) -> None:
    with open(filepath, 'wb') as f:
        f.write(data)


def read_string_from_file(filepath: str):
    with open(filepath, "r") as f:
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
comfyHost, comfyPort = opts.COMFY_ADDRESS.split(':')
if comfyHost in ["0.0.0.0", "127.0.0.1", "localhost"]:
    frontendComfyLink = f"buildLocalLink({comfyPort})"
else:
    frontendComfyLink = f'"http://{opts.COMFY_ADDRESS}"'
ifaceCustomHead = (
    "<script>"
        f"const COMFY_ADDRESS = {frontendComfyLink};\n\n"
        f"{ifaceJS}\n\n"
    "</script>"
)
logoPath = os.path.join(MCWW_WEB_DIR, 'logo.svg')
logoHtml = read_string_from_file(logoPath)


def get_image_hash(image: Image.Image) -> str:
    image_bytes = image.tobytes()
    hasher = hashlib.sha256()
    hasher.update(image_bytes)
    return hasher.hexdigest()[:20]


def raiseGradioError(e: Exception) -> Never:
    text = f"{e.__class__.__name__}: {e}"
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
        print(f"Unexpected error while parsing git commit: {e.__class__.__name__}: {e}")
        return None

def getStorageKey():
    key = f"{getGitCommit()}/{str(opts.FILE_CONFIG.mode)}"
    print(f"browser storage key is {key}")
    return key

def getStorageEncryptionKey():
    file = os.path.join(MCWW_WEB_DIR, '..', 'browser_storage_encryption_key')
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

class ASGIExceptionFilter(logging.Filter):
    def filter(self, record):
        return "Exception in ASGI application" not in record.getMessage()
logging.getLogger("uvicorn").addFilter(ASGIExceptionFilter())
logging.getLogger("uvicorn.error").addFilter(ASGIExceptionFilter())
logging.getLogger("uvicorn.access").addFilter(ASGIExceptionFilter())
logging.getLogger("starlette").addFilter(ASGIExceptionFilter())
logging.getLogger("fastapi").addFilter(ASGIExceptionFilter())

