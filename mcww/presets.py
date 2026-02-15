import os, json
import gradio as gr
from wrapt import synchronized
from mcww import opts
from mcww.utils import (read_string_from_file, save_string_to_file, saveLogError,
    moveKeyUp, moveKeyDown, filterList,
)


class Presets:
    def __init__(self, workflowName: str):
        self._inner: dict[str, dict[str, str]] = dict()
        self._presetsFilePath = os.path.join(opts.STORAGE_DIRECTORY, 'presets', f'{workflowName}.json')
        os.makedirs(os.path.dirname(self._presetsFilePath), exist_ok=True)
        if os.path.exists(self._presetsFilePath):
            try:
                self._inner = json.loads(read_string_from_file(self._presetsFilePath))
            except Exception as e:
                text = f"Can't load preset from '{self._presetsFilePath}'"
                gr.Warning(text)
                saveLogError(e, text)

    @synchronized
    def save(self):
        save_string_to_file(json.dumps(self._inner, indent=4), self._presetsFilePath)

    @synchronized
    def getPresetNames(self, filter: str = ""):
        return filterList(filter, list(self._inner.keys()))

    @synchronized
    def addPresetName(self, newName: str):
        if newName in self._inner:
            raise gr.Error(f'New preset name "{newName}" is already in presets', duration=1, print_exception=False)
        self._inner[newName] = dict[str, str]()

    @synchronized
    def deletePresetName(self, preset: str):
        del self._inner[preset]

    @synchronized
    def renamePreset(self, oldName: str, newName: str):
        if oldName == newName:
            return
        if newName in self._inner:
            raise gr.Error(f'New preset name "{newName}" is already in presets', duration=1, print_exception=False)
        self._inner = {newName if key == oldName else key : self._inner[key] for key in self._inner.keys()}

    @synchronized
    def getPromptValue(self, preset: str, elementKey: str):
        return self._inner[preset].get(elementKey, "")

    @synchronized
    def getAllKeys(self, preset: str):
        return set(self._inner[preset].keys())

    @synchronized
    def deleteKey(self, preset: str, elementKey: str):
        if elementKey in self._inner[preset]:
            del self._inner[preset][elementKey]

    @synchronized
    def setPromptValue(self, preset: str, elementKey: str, value: str):
        self._inner[preset][elementKey] = value

    @synchronized
    def getPromptsInSamplesFormat(self, elementKeys: list[str], filter: str = ""):
        result: list[list[str]] = []
        for preset in self.getPresetNames(filter=filter):
            result.append([self.getPromptValue(preset, elementKey) for elementKey in elementKeys])
        return result

    @synchronized
    def moveUp(self, preset: str):
        self._inner = moveKeyUp(self._inner, preset)

    @synchronized
    def moveDown(self, preset: str):
        self._inner = moveKeyDown(self._inner, preset)

    @synchronized
    def applyNewOrder(self, newOrder: list[str]):
        oldLabels = set(self._inner.keys())
        newLabels = set(newOrder)
        if newLabels != oldLabels:
            raise gr.Error(f"New labels and old labels are different sets: {oldLabels}, {newLabels}")
        self._inner = {key : self._inner[key] for key in newOrder}

