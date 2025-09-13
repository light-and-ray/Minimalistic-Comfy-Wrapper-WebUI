from typing import Never


import re, os, hashlib
from settings import SRC_DIRECTORY
from PIL import Image
import gradio as gr

def save_string_to_file(data: str, filepath: str) -> bool:
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        return True
    except IOError as e:
        print(f"Error saving file to {filepath}: {e}")
        return False

def read_string_from_file(filepath: str):
    with open(filepath, "r") as f:
        return f.read()


def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split('([0-9]+)', s)
    ]


_jsScriptPath = os.path.join(SRC_DIRECTORY, '..', 'script.js')
onIfaceLoadedInjectJS = ('(...args) => {'
f'   {read_string_from_file(_jsScriptPath)}'
'    return [...args];'
'}')

_cssStylePath = os.path.join(SRC_DIRECTORY, '..', 'style.css')
ifaceCSS = read_string_from_file(_cssStylePath)



def get_image_hash(image: Image.Image) -> str:
    image_bytes = image.tobytes()
    hasher = hashlib.sha256()
    hasher.update(image_bytes)
    return hasher.hexdigest()[:20]


def raiseGradioError(e: Exception) -> Never:
    text = f"{e.__class__.__name__}: {e}"
    print(text)
    raise gr.Error(text[:100])

