import os, traceback, random, uuid, re, json
import gradio as gr
from mcww import opts
from mcww.utils import read_string_from_file, save_string_to_file


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

easterEggWolf3dIframe = f'''
<iframe
    src="{os.getenv("WOLF_3D_URL", "https://git.nihilogic.dk/wolf3d/")}"
    width="640"
    height="480"
    frameborder="0"
    allowfullscreen
></iframe>
'''

MAIN_UI_PAGES = ["queue", "project", "helpers", "settings", "compare", "wolf3d"]


def showRenderingErrorGradio(e):
    stack_trace = getattr(e, "stack_trace", None)
    if not stack_trace:
        stack_trace = traceback.format_exc()
    gr.Markdown(f"Critical error on rendering, report it on github\n\n"
                    f"{e.__class__.__name__}: {e}\n\n"
                    f"```\n{stack_trace}\n```\n",
            elem_classes=["mcww-visible"])


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


def extractMetadata(filepath: str):
    if not filepath:
        return None, None
    with open(filepath, 'rb') as f:
        data = f.read()
    pattern = rb'\{([\x20-\x7E]{100,})\}'
    strings = re.findall(pattern, data)
    strings: list[str] = [s.decode('ascii') for s in strings]
    strings = sorted(strings, key=lambda s: len(s), reverse=True)
    prompt = None
    workflow = None
    for string in strings:
        try:
            string = '{' + string + '}'
            metadata = json.loads(string)
            if "nodes" in metadata:
                workflow = metadata
            else:
                prompt = metadata
        except json.JSONDecodeError:
            pass
    return prompt, workflow
