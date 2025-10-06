from mcww.workflowUI import WorkflowUI
import json

class WorkflowState:
    def __init__(self, stateDict: dict):
        assert "inputs" in stateDict
        self._stateDict = stateDict

    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        print("setValuesToWorkflowUI:")
        for elementUI in workflowUI.inputElements:
            key = f"{elementUI.element.getKey()}/{workflowUI.name}"
            if key in self._stateDict['inputs']:
                elementUI.gradioComponent.value = self._stateDict['inputs'][key]
        print(json.dumps(self._stateDict, indent=2))

    @staticmethod
    def getWorkflowUIStateKwargs(workflowUI: WorkflowUI, oldState):
        inputKeys = [f"{x.element.getKey()}/{workflowUI.name}" for x in workflowUI.inputElements]
        def getWorkflowUIState(*values):
            if oldState is None:
                stateDict = {"inputs": {}}
            else:
                stateDict = oldState._stateDict
            for inputKey, inputValue in zip(inputKeys, values):
                stateDict["inputs"][inputKey] = inputValue
            return WorkflowState(stateDict)

        kwargs = dict(
            fn=getWorkflowUIState,
            inputs=[x.gradioComponent for x in workflowUI.inputElements],
        )
        return kwargs

