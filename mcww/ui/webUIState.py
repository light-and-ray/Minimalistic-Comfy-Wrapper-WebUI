import json, uuid, copy
import gradio as gr
from gradio.components.gallery import GalleryImage, GalleryVideo
from wrapt import synchronized
from mcww.comfy.comfyUtils import ComfyIsNotAvailable
from mcww.ui.workflowUI import ElementUI, WorkflowUI
from mcww.comfy.comfyFile import getUploadedComfyFileIfReady
from mcww.comfy.nodeUtils import toGradioPayload
from mcww.utils import DataType, saveLogError


def needSave(elementUI: ElementUI):
    if elementUI.element.category == "output" and elementUI.element.field.type in (DataType.VIDEO, DataType.AUDIO):
        return False
    return True


def replaceIfUploaded(obj):
    try:
        if isinstance(obj, list):
            return [replaceIfUploaded(x) for x in obj]
        if not isinstance(obj, dict):
            return obj
        for key in ("image", "video"):
            if key in obj:
                obj[key] = replaceIfUploaded(obj[key])
                return obj
        comfyFile = getUploadedComfyFileIfReady(obj["path"], False)
        if comfyFile is None:
            return obj
        obj = comfyFile.getGradioInputForComponentInit()
        for key in ("image", "video"):
            if key in obj:
                obj = obj[key]
                break
        return obj
    except (ComfyIsNotAvailable, FileNotFoundError):
        return obj


class ProjectState:
    DEFAULT_STATE_DICT = {
                'elements' : {},
                'selectedWorkflow': None,
                'projectId' : str(uuid.uuid4()),
            }

    def __init__(self, stateDict: dict|None):
        if stateDict:
            self._stateDict = stateDict
        else:
            self._stateDict = self.DEFAULT_STATE_DICT

    @staticmethod
    def getElementUISaveKey(elementUI: ElementUI, workflowUI: WorkflowUI):
        return f"{elementUI.element.getKey()}/{elementUI.extraKey}/{workflowUI.name}"

    @staticmethod
    def getBatchCountSaveKey(workflowUI: WorkflowUI):
        return f'_batchCount/{workflowUI.name}'

    @synchronized
    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        elementsUI = workflowUI.inputElements + workflowUI.mediaSingleElements + \
                workflowUI.mediaBatchElements + workflowUI.outputElements
        for elementUI in elementsUI:
            key = self.getElementUISaveKey(elementUI, workflowUI)
            if key in self._stateDict['elements']:
                obj = self._stateDict['elements'][key]
                obj = replaceIfUploaded(obj)
                elementUI.gradioComponent.value = obj
        key = self.getBatchCountSaveKey(workflowUI)
        if key in self._stateDict['elements']:
            workflowUI.batchCountComponent.value = self._stateDict['elements'][key]

    @synchronized
    def getSelectedWorkflow(self):
        return self._stateDict["selectedWorkflow"]

    @synchronized
    def setSelectedWorkflow(self, name):
        self._stateDict["selectedWorkflow"] = name

    @synchronized
    def getProjectId(self):
        return self._stateDict["projectId"]

    @synchronized
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

    @synchronized
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

    @synchronized
    def getActiveProject(self):
        if self._activeProjectNum < 0 or self._activeProjectNum >= len(self._projects):
            self._activeProjectNum = 0
        if len(self._projects) == 0:
            self._projects += [ProjectState(None)]
        return self._projects[self._activeProjectNum]

    @synchronized
    def replaceActiveProject(self, projectState: ProjectState):
        self._projects[self._activeProjectNum] = projectState

    @synchronized
    def toJson(self):
        json_ = {
            "activeProjectNum" : self._activeProjectNum,
            "projects" : [],
        }
        for project in self._projects:
            json_["projects"].append(project._stateDict)
        return json.dumps(json_)

    @synchronized
    def _getProjectsRadio(self):
        radio = gr.Radio(choices=[f'#{x}' for x in range(len(self._projects))],
                        value=f'#{self._activeProjectNum}')
        return radio

    DEFAULT_WEBUI_STATE_JSON = json.dumps({
                        "activeProjectNum": 0,
                        "projects": [None],
                    })

    @synchronized
    def getActiveWorkflowStateKwags(self, workflowUI: WorkflowUI) -> dict:
        elementsUI = workflowUI.inputElements + workflowUI.mediaSingleElements + \
                workflowUI.mediaBatchElements + workflowUI.outputElements
        oldActiveProjectState = self.getActiveProject()
        def getActiveWorkflowState(batchCount: int, *values):
            try:
                if oldActiveProjectState is None:
                    newStateDict = ProjectState.DEFAULT_STATE_DICT
                else:
                    newStateDict = oldActiveProjectState._stateDict
                for elementUI, value in zip(elementsUI, values):
                    if not needSave(elementUI):
                        continue
                    key = ProjectState.getElementUISaveKey(elementUI, workflowUI)
                    value = replaceIfUploaded(value)
                    newStateDict["elements"][key] = value
                batchCountKey = ProjectState.getBatchCountSaveKey(workflowUI)
                newStateDict["elements"][batchCountKey] = batchCount
                self.replaceActiveProject(ProjectState(newStateDict))
                return self.toJson()
            except Exception as e:
                text = "Unexpected exception auto save. It's a critical error, please report it on github"
                saveLogError(e, text)
                raise gr.Error(text, print_exception=False)

        kwargs = dict(
            fn=getActiveWorkflowState,
            inputs=[workflowUI.batchCountComponent] + [x.gradioComponent for x in elementsUI],
            preprocess=False,
            show_progress="hidden",
        )
        return kwargs

    @synchronized
    def onSelectWorkflow(self, name):
        activeProjectState: ProjectState = self.getActiveProject()
        activeProjectState.setSelectedWorkflow(name)
        self.replaceActiveProject(projectState=activeProjectState)
        return self.toJson()

