from mcww.workflowUI import WorkflowUI
import json
import gradio as gr

class WorkflowState:
    def __init__(self, stateDict: dict|None):
        if stateDict:
            self._stateDict = stateDict
        else:
            self._stateDict = {'elements' : {}, 'selectedWorkflow': None}

    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        for elementUI in workflowUI.inputElements + workflowUI.outputElements:
            key = f"{elementUI.element.getKey()}/{workflowUI.name}"
            if key in self._stateDict['elements']:
                elementUI.gradioComponent.value = self._stateDict['elements'][key]

    def getSelectedWorkflow(self):
        return self._stateDict["selectedWorkflow"]


class WorkflowStates:
    def __init__(self, states):
        statesJson = json.loads(states)
        self._statesList = []
        for stateDict in statesJson["states"]:
            self._statesList.append(WorkflowState(stateDict))
        self._selected = statesJson["selected"]

    @staticmethod
    def _onSelected(states, selected: str):
        states = WorkflowStates(states)
        states._selected = int(selected.removeprefix('#'))
        return states.toJson(), states.toRadio()

    @staticmethod
    def _onNewButtonClicked(states):
        states = WorkflowStates(states)
        states._statesList += [WorkflowState(None)]
        states._selected = len(states._statesList) - 1
        return states.toJson(), states.toRadio()

    def getSelectedWorkflowState(self):
        return self._statesList[self._selected]

    def replaceSelected(self, state: WorkflowState):
        self._statesList[self._selected] = state

    def toJson(self):
        json_ = {
            "selected" : self._selected,
            "states" : []
        }
        for state in self._statesList:
            json_["states"].append(state._stateDict)
        return json.dumps(json_)

    def toRadio(self):
        radio = gr.Radio(choices=[f'#{x}' for x in range(len(self._statesList))],
                        value=f'#{self._selected}')
        return radio

    DEFAULT_STATES_JSON = json.dumps({"selected": 0, "states": [None]})

    def getSaveStatesKwargs(self, workflowUI: WorkflowUI) -> dict:
        elements = workflowUI.inputElements + workflowUI.outputElements
        keys = [f"{x.element.getKey()}/{workflowUI.name}" for x in elements]
        oldState = self.getSelectedWorkflowState()
        def getWorkflowUIState(*values):
            if oldState is None:
                stateDict = {"elements": {}}
            else:
                stateDict = oldState._stateDict
            for key, value in zip(keys, values):
                stateDict["elements"][key] = value
            self.replaceSelected(WorkflowState(stateDict))
            return self.toJson()

        kwargs = dict(
            fn=getWorkflowUIState,
            inputs=[x.gradioComponent for x in elements],
            preprocess=False,
            show_progress="hidden",
        )
        return kwargs

