from typing import Any


from mcww.workflowUI import WorkflowUI
import json, copy
import gradio as gr

class WorkflowState:
    def __init__(self, stateDict: dict|None):
        if stateDict:
            self._stateDict = stateDict
        else:
            self._stateDict = {'elements' : {}}

    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        for elementUI in workflowUI.inputElements + workflowUI.outputElements:
            key = f"{elementUI.element.getKey()}/{workflowUI.name}"
            if key in self._stateDict['elements']:
                elementUI.gradioComponent.value = self._stateDict['elements'][key]

    @staticmethod
    def getWorkflowUIStateKwargs(workflowUI: WorkflowUI, states: 'WorkflowStates'):
        elements = workflowUI.inputElements + workflowUI.outputElements
        keys = [f"{x.element.getKey()}/{workflowUI.name}" for x in elements]
        oldState = states.getSelectedWorkflowState()
        def getWorkflowUIState(*values):
            if oldState is None:
                stateDict = {"elements": {}}
            else:
                stateDict = oldState._stateDict
            for key, value in zip(keys, values):
                stateDict["elements"][key] = value
            states.replaceSelected(WorkflowState(stateDict))
            return states.toJson()

        kwargs = dict(
            fn=getWorkflowUIState,
            inputs=[x.gradioComponent for x in elements],
            preprocess=False,
            show_progress=False,
        )
        return kwargs


class WorkflowStates:
    def __init__(self, states: gr.BrowserState):
        statesJson = json.loads(states)
        self._statesList = []
        for stateDict in statesJson["states"]:
            self._statesList.append(WorkflowState(stateDict))
        self._selected = statesJson["selected"]

    def _onSelected(self, selected: str):
        self._selected = int(selected.removeprefix('#'))
        return self.toJson()

    def _onNewButtonClicked(self):
        self._statesList += [WorkflowState(None)]
        self._selected = len(self._statesList) - 1
        return self.toJson()

    def render(self, linkedComponent: gr.State, refreshWorkflowUIKwargs: dict):
        radio = gr.Radio(show_label=False,
                choices=[f'#{x}' for x in range(len(self._statesList))],
                value=f'#{self._selected}'
            )
        radio.select(
            fn=self._onSelected,
            inputs=[radio],
            outputs=[linkedComponent]
        ).then(
            **refreshWorkflowUIKwargs
        )
        newButton = gr.Button("+")
        newButton.click(
            fn=self._onNewButtonClicked,
            outputs=[linkedComponent],
        ).then(
            **refreshWorkflowUIKwargs
        )

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

    DEFAULT_STATES_JSON = '{"selected": 0, "states": [null]}'
