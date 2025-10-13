from dataclasses import dataclass
import websocket, time
import urllib.request, urllib.parse
from PIL import Image
import gradio as gr
import io, requests, uuid, json, os, concurrent
from mcww import opts
from mcww.utils import get_image_hash, save_binary_to_file
from gradio.components.gallery import GalleryImage
from gradio.data_classes import ImageData


client_id = str(uuid.uuid4())

class ComfyUIException(Exception):
    pass


@dataclass
class ComfyFile:
    filename: str
    subfolder: str
    folder_type: str

    def _getCaption(self):
        caption = self.filename
        if self.subfolder:
            caption = f"{self.subfolder}/{caption}"
        return caption


    def _getDirectLink(self):
        data = {"filename": self.filename, "subfolder": self.subfolder, "type": self.folder_type}
        url_values = urllib.parse.urlencode(data)
        url = f"http://{opts.COMFY_ADDRESS}/view?{url_values}"
        return url


    def _getFile(self):
        with urllib.request.urlopen(self._getDirectLink()) as response:
            return response.read()


    def _getPilImage(self):
        image = Image.open(io.BytesIO(self._getFile()))
        return image


    def _getFilePath(self):
        if opts.FILE_CONFIG.mode == opts.FilesMode.DIRECT_LINKS:
            raise Exception("Wrong mode")
        if self.folder_type == "input":
            dir = opts.FILE_CONFIG.input_dir
        elif self.folder_type == "output":
            dir = opts.FILE_CONFIG.output_dir
        else:
            raise Exception(f"Unknown {self.folder_type=}")
        return os.path.join(dir, self.subfolder, self.filename)


    def _ensureFileExists(self):
        filePath = self._getFilePath()
        if opts.FILE_CONFIG.mode == opts.FilesMode.SAME_SERVER:
            if not os.path.exists(filePath):
                raise Exception(f"File {filePath} doesn't exist in same_server mode")
        elif opts.FILE_CONFIG.mode == opts.FilesMode.MIRROR:
            if not os.path.exists(filePath):
                fileData = self._getFile()
                os.makedirs(os.path.dirname(filePath), exist_ok=True)
                save_binary_to_file(fileData, filePath)


    def getUrl(self):
        if opts.FILE_CONFIG.mode == opts.FilesMode.DIRECT_LINKS:
            url=self._getDirectLink()
        else:
            self._ensureFileExists()
            url=f"/gradio_api/file={self._getFilePath()}"
        return url


    def getGradioGallery(self):
        if self.filename.endswith(".png"):
            url = self.getUrl()
            image: ImageData = ImageData(url=url, orig_name=self.filename)
            caption = None
            if opts.showNamesInGallery:
                caption - self._getCaption()
            return GalleryImage(image=image, caption=caption)
        else:
            pass
        raise Exception("Not implemented getGradioGallery for this Comfy file type")


def queue_prompt(prompt, prompt_id):
    p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{opts.COMFY_ADDRESS}/prompt", data=data)
    urllib.request.urlopen(req).read()


def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{opts.COMFY_ADDRESS}/history/{prompt_id}") as response:
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
                comfyFile = ComfyFile(
                    filename=image['filename'],
                    subfolder=image['subfolder'],
                    folder_type=image['type']
                )
                images_output.append(comfyFile)
        output_images[node_id] = images_output

    return output_images


def _uploadImageToComfySync(pil_image: Image.Image) -> ComfyFile:
    filename_prefix = "pil_upload"
    filename_prefix = filename_prefix.removesuffix(".json")
    url = f"http://{opts.COMFY_ADDRESS}/upload/image"
    filename = f"{filename_prefix}_{get_image_hash(pil_image)}.png"
    image_stream = io.BytesIO()
    try:
        pil_image.save(image_stream, format='PNG')
        image_stream.seek(0)
        files = {'image': (filename, image_stream, 'image/png')}
        response = requests.post(url, files=files)
        response.raise_for_status()
        response = response.json()
        return ComfyFile(response["name"], response["subfolder"], response["type"])
    finally:
        image_stream.close()


g_uploadedFilesFutures: dict[str, concurrent.futures.Future] = {}
g_uploadedFilesResults: dict[str, ComfyFile] = {}  # Store results when done

def _startUploadInBackground(path: str) -> None:
    def upload_wrapper():
        pil_image = Image.open(path)
        result = _uploadImageToComfySync(pil_image)
        g_uploadedFilesResults[path] = result

    future = concurrent.futures.ThreadPoolExecutor().submit(upload_wrapper)
    g_uploadedFilesFutures[path] = future


def getUploadedComfyFileIfReady(path: str) -> ComfyFile|None:
    """Checks if the file is already uploaded (or upload is done)."""
    if path in g_uploadedFilesResults:
        # gr.Info(f"Done {path}")
        return g_uploadedFilesResults[path]
    elif path in g_uploadedFilesFutures:
        return None
    else:
        _startUploadInBackground(path)
        return None


def getUploadedComfyFile(path: str) -> ComfyFile:
    file = None
    while file is None:
        file = getUploadedComfyFileIfReady(path)
        time.sleep(0.05)
    return file


def processComfy(workflow: str) -> dict:
    ws = websocket.WebSocket()
    ws.connect(f"ws://{opts.COMFY_ADDRESS}/ws?clientId={client_id}")
    nodes = get_images(ws, workflow)
    ws.close()
    return nodes


