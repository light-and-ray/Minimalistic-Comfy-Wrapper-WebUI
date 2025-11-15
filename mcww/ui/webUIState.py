from gradio.components.gallery import GalleryImage, GalleryVideo
from gradio.data_classes import ImageData
from gradio.components.video import VideoData
import json, uuid, copy
import gradio as gr
from mcww.comfy.comfyUtils import ComfyIsNotAvailable
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.comfyFile import getUploadedComfyFileIfReady
from mcww.comfy.nodeUtils import toGradioPayload
from mcww.utils import saveLogError

def needToUploadAndReplace(obj):
    obj = toGradioPayload(obj)
    if isinstance(obj, ImageData):
        if obj.path:
            return True
    return False

def uploadAndReplace(obj: dict):
    try:
        comfyFile = getUploadedComfyFileIfReady(obj["path"])
        if comfyFile is None:
            return obj
        obj["path"] = None
        gallery = comfyFile.getGradioGallery()
        if isinstance(gallery, GalleryImage):
            obj["url"] = gallery.image.url
            obj["orig_name"] = gallery.image.orig_name
        return obj
    except ComfyIsNotAvailable:
        return obj


class ProjectState:
    def __init__(self, stateDict: dict|None):
        if stateDict:
            self._stateDict = stateDict
        else:
            self._stateDict = {
                'elements' : {},
                'selectedWorkflow': None,
                'projectId' : str(uuid.uuid4())
            }

    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        for elementUI in workflowUI.inputElements + workflowUI.outputElements:
            key = f"{elementUI.element.getKey()}/{workflowUI.name}"
            if key in self._stateDict['elements']:
                obj = self._stateDict['elements'][key]
                if needToUploadAndReplace(obj):
                    obj = uploadAndReplace(obj)
                elementUI.gradioComponent.value = obj

    def getSelectedWorkflow(self):
        return self._stateDict["selectedWorkflow"]

    def setSelectedWorkflow(self, name):
        self._stateDict["selectedWorkflow"] = name

    def getProjectId(self):
        return self._stateDict["projectId"]

    def recreateProjectId(self):
        self._stateDict["projectId"] = str(uuid.uuid4())


class WebUIState:
    def __init__(self, webUIStateJson):
        try:
            webUIStateJson: dict = json.loads(webUIStateJson)
            self._projects: list[ProjectState] = []
            for stateDict in webUIStateJson["projects"]:
                self._projects.append(ProjectState(stateDict))
            self._activeProjectNum: int = webUIStateJson["activeProjectNum"]
        except Exception as e:
            saveLogError(e, "Error on loading webUiState, resetting to default")
            self.__init__(self.DEFAULT_WEBUI_STATE_JSON)

    @staticmethod
    def onProjectSelected(webUIStateJson, selected: str|None = None):
        webUIState = WebUIState(webUIStateJson)
        if selected:
            webUIState._activeProjectNum = int(selected.removeprefix('#'))
        return webUIState.toJson(), webUIState._getProjectsRadio()

    @staticmethod
    def onProjectClosed(webUIStateJson, index: str|None = None):
        webUIState = WebUIState(webUIStateJson)
        if webUIState._activeProjectNum == index:
            if len(webUIState._projects) <= 1:
                webUIState = WebUIState(WebUIState.DEFAULT_WEBUI_STATE_JSON)
                index = None
            if index == len(webUIState._projects) - 1:
                webUIState._activeProjectNum -= 1
        elif webUIState._activeProjectNum > index:
            webUIState._activeProjectNum -= 1
        if index is not None:
            del webUIState._projects[index]
        return webUIState.toJson(), webUIState._getProjectsRadio(), webUIState._getCloseProjectsRadio()

    @staticmethod
    def onGetCloseProjectsRadio(webUIStateJson):
        webUIState = WebUIState(webUIStateJson)
        return webUIState._getCloseProjectsRadio()

    def _getCloseProjectsRadio(self):
        return gr.Radio(choices=[x for x in range(len(self._projects))] + ["None"], value="None")

    @staticmethod
    def onNewProjectButtonClicked(webUIStateJson):
        webUIState = WebUIState(webUIStateJson)
        webUIState._projects += [ProjectState(None)]
        webUIState._activeProjectNum = len(webUIState._projects) - 1
        return webUIState.toJson(), webUIState._getProjectsRadio()

    @staticmethod
    def onCopyProjectButtonClicked(webUIStateJson):
        webUIState = WebUIState(webUIStateJson)
        newProjectState = copy.deepcopy(webUIState.getActiveProject())
        newProjectState.recreateProjectId()
        webUIState._projects += [newProjectState]
        webUIState._activeProjectNum = len(webUIState._projects) - 1
        return webUIState.toJson(), webUIState._getProjectsRadio()

    def getActiveProject(self):
        return self._projects[self._activeProjectNum]

    def replaceActiveProject(self, projectState: ProjectState):
        self._projects[self._activeProjectNum] = projectState

    def toJson(self):
        json_ = {
            "activeProjectNum" : self._activeProjectNum,
            "projects" : [],
        }
        for project in self._projects:
            json_["projects"].append(project._stateDict)
        return json.dumps(json_)

    def _getProjectsRadio(self):
        radio = gr.Radio(choices=[f'#{x}' for x in range(len(self._projects))],
                        value=f'#{self._activeProjectNum}')
        return radio

    DEFAULT_WEBUI_STATE_JSON = json.dumps({
                        "activeProjectNum": 0,
                        "projects": [None],
                    })

    def getActiveWorkflowStateKwags(self, workflowUI: WorkflowUI) -> dict:
        elements = workflowUI.inputElements + workflowUI.outputElements
        keys = [f"{x.element.getKey()}/{workflowUI.name}" for x in elements]
        oldActiveProjectState = self.getActiveProject()
        def getActiveWorkflowState(*values):
            if oldActiveProjectState is None:
                newStateDict = {"elements": {}}
            else:
                newStateDict = oldActiveProjectState._stateDict
            for key, value in zip(keys, values):
                if needToUploadAndReplace(value):
                    value = uploadAndReplace(value)
                newStateDict["elements"][key] = value
            self.replaceActiveProject(ProjectState(newStateDict))
            return self.toJson()

        kwargs = dict(
            fn=getActiveWorkflowState,
            inputs=[x.gradioComponent for x in elements],
            preprocess=False,
            show_progress="hidden",
        )
        return kwargs

    def onSelectWorkflow(self, name):
        activeProjectState: ProjectState = self.getActiveProject()
        activeProjectState.setSelectedWorkflow(name)
        self.replaceActiveProject(activeProjectState)
        return self.toJson()

