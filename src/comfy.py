import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io
from settings import COMFY_ADDRESS
from utils import get_image_hash
import requests

client_id = str(uuid.uuid4())

class ComfyUIException(Exception):
    pass

def queue_prompt(prompt, prompt_id):
    p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(COMFY_ADDRESS), data=data)
    urllib.request.urlopen(req).read()

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    url = "http://{}/view?{}".format(COMFY_ADDRESS, url_values)
    with urllib.request.urlopen(url) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(COMFY_ADDRESS, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = str(uuid.uuid4())
    queue_prompt(prompt, prompt_id)
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done

    history = get_history(prompt_id)[prompt_id]
    status = history["status"]["status_str"]

    if status == "error":
        for message in history["status"]["messages"]:
            if message[0] == "execution_error":
                raise ComfyUIException(message[1]["exception_type"] + ": " + message[1]["exception_message"])
    elif status != "success":
        print(json.dumps(history["status"], indent=2))
        raise Exception(f"Unknown ComfyUI status: {status}")

    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                image_data = Image.open(io.BytesIO(image_data))
                image_data._mcww_filename = image['filename']
                caption = image['filename']
                if image['subfolder']:
                    caption = image['subfolder'] + "/" + caption
                images_output.append((image_data, caption))
        output_images[node_id] = images_output

    return output_images


def upload_image_to_comfy(pil_image: Image.Image, filename_prefix: str = "pil_upload"):
    if not isinstance(pil_image, Image.Image):
        return False, "Error: Input must be a Pillow Image object."
    filename_prefix = filename_prefix.removesuffix(".json")
    url = f"http://{COMFY_ADDRESS}/upload/image"
    filename = f"{filename_prefix}_{get_image_hash(pil_image)}.png"
    image_stream = io.BytesIO()
    pil_image.save(image_stream, format='PNG')
    image_stream.seek(0)
    files = {'image': (filename, image_stream, 'image/png')}

    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        try:
            response_data = response.json()
            return True, response_data
        except json.JSONDecodeError:
            return False, f"Error: Failed to decode JSON from response. Response content: {response.text}"

    except requests.exceptions.RequestException as e:
        return False, f"Error during image upload: {e}"


def processComfy(workflow: str) -> dict:
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(COMFY_ADDRESS, client_id))
    nodes = get_images(ws, workflow)
    ws.close()
    return nodes


