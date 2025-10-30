from dataclasses import dataclass
import urllib.request, urllib.parse
import io, requests, os, concurrent, time
from PIL import Image
from mcww import opts
from mcww.utils import (save_binary_to_file, DataType, isVideoExtension, isImageExtension,
    read_binary_from_file
)
from mcww.comfy.comfyUtils import getHttpComfyPathUrl, checkForComfyIsNotAvailable
from gradio.components.gallery import GalleryImage, GalleryVideo
from gradio.data_classes import ImageData, FileData
from gradio.utils import get_upload_folder


@dataclass
class ComfyFile:
    filename: str
    subfolder: str
    folder_type: str

    def getDataType(self) -> DataType:
        if isImageExtension(self.filename):
            return DataType.IMAGE
        if isVideoExtension(self.filename):
            return DataType.VIDEO
        raise Exception(f"Unknown DataType for ComfyFile {self}")


    def _getCaption(self):
        caption = self.filename
        if self.subfolder:
            caption = f"{self.subfolder}/{caption}"
        return caption


    def _getDirectLink(self):
        data = {"filename": self.filename, "subfolder": self.subfolder, "type": self.folder_type}
        url_values = urllib.parse.urlencode(data)
        url = getHttpComfyPathUrl(f"/view?{url_values}")
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
        if self.getDataType() == DataType.IMAGE:
            url = self.getUrl()
            image: ImageData = ImageData(url=url, orig_name=self.filename)
            caption = None
            if opts.showNamesInGallery:
                caption - self._getCaption()
            return GalleryImage(image=image, caption=caption)
        elif self.getDataType() == DataType.VIDEO:
            url = self.getUrl()
            video: FileData = FileData(path=get_upload_folder(), url=url, orig_name=self.filename)
            caption = None
            if opts.showNamesInGallery:
                caption - self._getCaption()
            return GalleryVideo(video=video, caption=caption)

        raise Exception("Not implemented getGradioGallery for this Comfy file type")


def _uploadFileToComfySync(path) -> ComfyFile:
    url = getHttpComfyPathUrl(f"/upload/image")
    filename = os.path.basename(path)
    file_stream = io.BytesIO(read_binary_from_file(path))
    try:
        file_stream.seek(0)
        files = {
            'image': (filename, file_stream),
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        response = response.json()
        return ComfyFile(response["name"], response["subfolder"], response["type"])
    except Exception as e:
        checkForComfyIsNotAvailable(e)
        raise
    finally:
        file_stream.close()


g_uploadedFilesFutures: dict[str, concurrent.futures.Future] = {}
g_uploadedFilesResults: dict[str, ComfyFile] = {}  # Store results when done

def _startUploadInBackground(path: str) -> None:
    def upload_wrapper():
        result = _uploadFileToComfySync(path)
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

