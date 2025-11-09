import gradio as gr
STUB = {
            "test1": {
                "promptElementKey": "Transform the image"
            },
            "test2": {
                "promptElementKey": "Transform the image"
            },
        }

class Presets:
    def __init__(self, workflowName: str):
        self._inner: dict[str, dict[str, str]] = STUB


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


