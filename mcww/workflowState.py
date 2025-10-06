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
            return states

        kwargs = dict(
            fn=getWorkflowUIState,
            inputs=[x.gradioComponent for x in elements],
            preprocess=False,
        )
        return kwargs


class WorkflowStates:
    def __init__(self):
        self._statesList: list[WorkflowState|None] = [WorkflowState(None)]
        self._selected = 0

    def _onSelected(self, selected: str):
        self._selected = int(selected.removeprefix('#'))
        return copy.deepcopy(self)

    def _onNewButtonClicked(self):
        self._statesList += [WorkflowState(None)]
        self._selected = len(self._statesList) - 1
        return copy.deepcopy(self)

    def render(self, linkedComponent: gr.State):
        radio = gr.Radio(show_label=False,
                choices=[f'#{x}' for x in range(len(self._statesList))],
                value=f'#{self._selected}'
            )
        radio.select(
            fn=self._onSelected,
            inputs=[radio],
            outputs=[linkedComponent]
        )
        newButton = gr.Button("+")
        newButton.click(
            fn=self._onNewButtonClicked,
            outputs=[linkedComponent],
        )

    def getSelectedWorkflowState(self):
        return self._statesList[self._selected]

    def replaceSelected(self, state: WorkflowState):
        self._statesList[self._selected] = state
