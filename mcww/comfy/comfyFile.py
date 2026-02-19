from dataclasses import dataclass
import urllib.parse
from gradio.components.video import VideoData
import io, requests, os, concurrent, time, json
from PIL import Image
from mcww import opts
from mcww.utils import (save_binary_to_file, DataType, isVideoExtension, isImageExtension,
    read_binary_from_file, isAudioExtension,
)
from mcww.comfy.comfyUtils import getHttpComfyPathUrl, checkForComfyIsNotAvailable, getNoFileUrl, getNoFilePath
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
        if isAudioExtension(self.filename):
            return DataType.AUDIO
        print(f"*** Unknown DataType for ComfyFile {self}. Assuming image")
        return DataType.IMAGE


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
        response = requests.get(self._getDirectLink())
        response.raise_for_status()
        return response.content


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
            try:
                self._ensureFileExists()
                url= f"/gradio_api/file={self._getFilePath()}"
            except Exception as e:
                url = getNoFileUrl(self.getDataType())
        return url


    def getGradioOutput(self):
        if self.getDataType() == DataType.IMAGE:
            url = self.getUrl()
            image: ImageData = ImageData(url=url, orig_name=self.filename, mime_type="image")
            return GalleryImage(image=image, caption=None)
        elif self.getDataType() == DataType.VIDEO:
            url = self.getUrl()
            video: FileData = FileData(path=get_upload_folder(), url=url, orig_name=self.filename, mime_type="video")
            return GalleryVideo(video=video, caption=None)
        elif self.getDataType() == DataType.AUDIO:
            url = self.getUrl()
            if opts.FILE_CONFIG.mode == opts.FilesMode.DIRECT_LINKS:
                print("*** audio is not supported in direct links server mode")
                path = get_upload_folder()
            else:
                path = self._getFilePath()
                if not os.path.exists(path):
                    path = getNoFilePath(DataType.AUDIO)
            audio: FileData = FileData(path=path, url=url, orig_name=self.filename, mime_type="audio")
            return audio
        raise Exception("Not implemented getGradioGallery for this Comfy file type")


    def getGradioInput(self):
        if self.getDataType() == DataType.IMAGE:
            url = self.getUrl()
            image: ImageData = ImageData(url=url, orig_name=self.filename, mime_type="image")
            return image
        elif self.getDataType() == DataType.VIDEO:
            url = self.getUrl()
            video: FileData = FileData(path=get_upload_folder(), url=url, orig_name=self.filename, mime_type="video")
            return VideoData(video=video)
        elif self.getDataType() == DataType.AUDIO:
            url = self.getUrl()
            audio: FileData = FileData(path=get_upload_folder(), url=url, orig_name=self.filename, mime_type="audio")
            return audio
        raise Exception("Not implemented getGradioMediaPayload for this Comfy file type")


    def getGradioOutputForComponentInit(self):
        return json.loads(self.getGradioOutput().model_dump_json())


    def getGradioInputForComponentInit(self):
        return json.loads(self.getGradioInput().model_dump_json())


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
g_uploadedFilesErrors: dict[str, Exception] = {}

def _startUploadInBackground(path: str) -> None:
    def upload_wrapper():
        try:
            result = _uploadFileToComfySync(path)
        except Exception as e:
            g_uploadedFilesErrors[path] = e
        else:
            g_uploadedFilesResults[path] = result

    future = concurrent.futures.ThreadPoolExecutor().submit(upload_wrapper)
    g_uploadedFilesFutures[path] = future


def getUploadedComfyFileIfReady(path: str, needStartDownload: bool = True) -> ComfyFile|None:
    """Checks if the file is already uploaded (or upload is done)."""
    if path in g_uploadedFilesErrors:
        e = g_uploadedFilesErrors[path]
        del g_uploadedFilesErrors[path]
        if path in g_uploadedFilesResults: del g_uploadedFilesResults[path]
        if path in g_uploadedFilesFutures: del g_uploadedFilesFutures[path]
        raise e
    if path in g_uploadedFilesResults:
        return g_uploadedFilesResults[path]
    elif path in g_uploadedFilesFutures:
        return None
    else:
        if needStartDownload:
            _startUploadInBackground(path)
        return None


def getUploadedComfyFile(path: str, needStartDownload: bool = True) -> ComfyFile:
    file = None
    while file is None:
        file = getUploadedComfyFileIfReady(path, needStartDownload)
        time.sleep(0.05)
    return file

