from typing import Never
import re, os, hashlib, traceback
import opts
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


_jsScriptPath = os.path.join(opts.SRC_DIRECTORY, '..', 'script.js')
ifaceCustomHead = f"<script>{read_string_from_file(_jsScriptPath)}</script>"

_cssStylePath = os.path.join(opts.SRC_DIRECTORY, '..', 'style.css')
ifaceCSS = read_string_from_file(_cssStylePath)



def get_image_hash(image: Image.Image) -> str:
    image_bytes = image.tobytes()
    hasher = hashlib.sha256()
    hasher.update(image_bytes)
    return hasher.hexdigest()[:20]


def raiseGradioError(e: Exception) -> Never:
    text = f"{e.__class__.__name__}: {e}"
    print(traceback.format_exc())
    raise gr.Error(text[:100], print_exception=False)


