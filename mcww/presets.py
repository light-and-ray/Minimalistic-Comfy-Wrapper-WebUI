
class Presets:
    def __init__(self, workflowName: str):
        self._inner: dict[str, dict[str, str]] ={
            "test1": {
                "promptElementKey": "Transform the image"
            },
            "test2": {
                "promptElementKey": "Transform the image"
            },
        }


    def getPresetNames(self):
        return list(self._inner.keys())


    def addPresetName(self, preset: str):
        self._inner[preset] = dict[str, str]


    def getPromptValue(self, preset: str, elementKey: str):
        return self._inner[preset].get(elementKey, "")


    def setPromptValue(self, preset: str, elementKey: str, value: str):
        self._inner[preset][elementKey] = value


