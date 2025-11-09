import os, json
import gradio as gr
from mcww import opts
from mcww.utils import (read_string_from_file, save_string_to_file, saveLogError,
    moveKeyUp, moveKeyDown
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


    def save(self):
        save_string_to_file(json.dumps(self._inner, indent=4), self._presetsFilePath)


    def getPresetNames(self):
        return list(self._inner.keys())


    def addPresetName(self, preset: str):
        self._inner[preset] = dict[str, str]()


    def deletePresetName(self, preset: str):
        del self._inner[preset]


    def renamePreset(self, oldName: str, newName: str):
        if oldName == newName:
            return
        if newName in self._inner:
            raise gr.Error(f"New preset name {newName} is already in presets", duration=1, print_exception=False)
        self._inner = {newName if key == oldName else key : self._inner[key] for key in self._inner.keys()}


    def getPromptValue(self, preset: str, elementKey: str):
        return self._inner[preset].get(elementKey, "")


    def setPromptValue(self, preset: str, elementKey: str, value: str):
        self._inner[preset][elementKey] = value


    def getPromptsInSamplesFormat(self, elementKeys: list[str]):
        result: list[list[str]] = []
        for preset in self.getPresetNames():
            result.append([self.getPromptValue(preset, elementKey) for elementKey in elementKeys])
        return result


    def moveUp(self, preset: str):
        self._inner = moveKeyUp(self._inner, preset)


    def moveDown(self, preset: str):
        self._inner = moveKeyDown(self._inner, preset)

