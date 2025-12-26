import os, random, re, json
from datetime import datetime
from dataclasses import asdict
import gradio as gr
from mcww import opts
from mcww.utils import read_binary_from_file, read_string_from_file, saveLogError, getJsStorageKey, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


MCWW_WEB_DIR = os.path.normpath(os.path.join(opts.MCWW_DIRECTORY, '..', 'mcww_web'))


def _concat_files(directory):
    # Process JS files: first from root, then from js/ subdir
    js_files = []
    # Look for JS files in the root directory
    for file in os.listdir(directory):
        if file.endswith('.js'):
            js_files.append(os.path.join(directory, file))
    # Look for JS files in the js/ subdirectory
    js_subdir = os.path.join(directory, 'js')
    if os.path.exists(js_subdir):
        for root, _, files in os.walk(js_subdir):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
    ifaceJS = "\n".join(read_string_from_file(f) for f in js_files)

    # Process CSS files: first from root, then from css/ subdir
    css_files = []
    # Look for CSS files in the root directory
    for file in os.listdir(directory):
        if file.endswith('.css'):
            css_files.append(os.path.join(directory, file))
    # Look for CSS files in the css/ subdirectory
    css_subdir = os.path.join(directory, 'css')
    if os.path.exists(css_subdir):
        for root, _, files in os.walk(css_subdir):
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
        saveLogError(e, "Unexpected error while preparing comfy frontend link")

    ifaceCustomHead = (
        '<meta name="viewport" content="width=device-width, initial-scale=1, interactive-widget=resizes-content">'
        "<script>"
            f"const COMFY_ADDRESS = {frontendComfyLink};\n\n"
            f"const QUEUE_SVG_ICON = `{read_string_from_file(os.path.join(MCWW_WEB_DIR, 'assets', 'queue.svg'))}`;\n\n"
            f"const STORAGE_KEY = '{getJsStorageKey()}';\n\n"
            f"const IMAGE_EXTENSIONS = {json.dumps(IMAGE_EXTENSIONS)};\n\n"
            f"const VIDEO_EXTENSIONS = {json.dumps(VIDEO_EXTENSIONS)};\n\n"
            f"const OPTIONS = {json.dumps(asdict(opts.options))};\n\n"
            f"{ifaceJS}\n\n"
        "</script>"
    )
    return ifaceCustomHead
logoPath = os.path.join(MCWW_WEB_DIR, 'logo.svg')
logoHtml = read_string_from_file(logoPath)
pwaIconPath = os.path.join(MCWW_WEB_DIR, 'pwa_icon.png')
pwaIconBytes = read_binary_from_file(pwaIconPath)


def getMcwwLoaderHTML(classes=[]):
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

def renderHolidaySpecial():
    try:
        today = datetime.now()
        if (today.month == 4 and today.day == 1):
            gr.Markdown("# Dead Internet Practice!", elem_classes=["mcww-visible", "horizontally-centred"])
        if (today.month == 12 and today.day == 25) or (today.month == 1 and today.day == 1):
            html = ""
            emojis = (['❄️']*90) + (['🌟']*3) + (['✨']*2) + (['🎄']*4) + (['🦌']*3)
            for emoji in emojis:
                left = random.randint(0, 100)
                top = random.randint(0, 100)
                size = random.randint(18, 20)
                html += f'<span style="left: {left}%; top: {top}%; font-size: {size}px;">{emoji}</span>'
            gr.HTML(html, elem_classes=["christmas-background"])
    except Exception as e:
        saveLogError(e, "error on renderHolidaySpecial")

easterEggWolf3dIframe = f'''
<iframe
    src="{os.getenv("WOLF_3D_URL", "https://git.nihilogic.dk/wolf3d/")}"
    width="640"
    height="480"
    frameborder="0"
    allowfullscreen
></iframe>
'''

MAIN_UI_PAGES = ["queue", "project", "helpers", "options", "compare", "presets", "image editor", "wolf3d"]


def showRenderingErrorGradio(e, prefix: str = ""):
    textCopy = saveLogError(e, prefix)
    gr.Markdown(f"Critical error on rendering, report it on github\n\n```\n{textCopy}\n```\n",
            elem_classes=["mcww-visible"])


def extractMetadata(filepath: str):
    if not filepath:
        return None, None
    with open(filepath, 'rb') as f:
        data = f.read()
    pattern = rb'\{([\x20-\x7E\t\r\n]{100,})\}'
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


class ButtonWithConfirm:
    def __init__(self, label, confirm_label="Confirm", cancel_label="Cancel", **kwargs):
        with gr.Row(elem_classes=["button-with-confirm-row"]):
            self.main_button = gr.Button(label, **kwargs)
            self.confirm_button = gr.Button(confirm_label, visible=False, variant="stop", **kwargs)
            kwargs["elem_classes"] = ["click-on-escape"] + kwargs.get("elem_classes", [])
            self.cancel_button = gr.Button(cancel_label, visible=False, **kwargs)

    def click(self, **kwargs):
        self.main_button.click(
            fn=lambda: [gr.update(visible=x) for x in [False, True, True]],
            outputs=[self.main_button, self.confirm_button, self.cancel_button],
        )
        result = self.confirm_button.click(
            fn=lambda: [gr.update(visible=x) for x in [True, False, False]],
            outputs=[self.main_button, self.confirm_button, self.cancel_button],
        ).then(
            **kwargs
        )
        self.cancel_button.click(
            fn=lambda: [gr.update(visible=x) for x in [True, False, False]],
            outputs=[self.main_button, self.confirm_button, self.cancel_button],
        )
        return result


def JsonTextbox(**kwargs):
    kwargs.setdefault('language', 'json')
    kwargs.setdefault('wrap_lines', True)
    kwargs.setdefault('max_lines', 30)
    if 'info' in kwargs:
        kwargs['label'] = f"{kwargs.get('label', '')} ({kwargs['info']})".strip()
        del kwargs['info']
        kwargs['show_label'] = True
    return gr.Code(**kwargs)

