from mcww.workflowUI import WorkflowUI
import json

class WorkflowState:
    def __init__(self, stateDict: dict):
        assert "elements" in stateDict
        self._stateDict = stateDict

    def setValuesToWorkflowUI(self, workflowUI: WorkflowUI):
        print("setValuesToWorkflowUI:")
        for elementUI in workflowUI.inputElements + workflowUI.outputElements:
            key = f"{elementUI.element.getKey()}/{workflowUI.name}"
            if key in self._stateDict['elements']:
                elementUI.gradioComponent.value = self._stateDict['elements'][key]
        # print(json.dumps(self._stateDict, indent=2))

    @staticmethod
    def getWorkflowUIStateKwargs(workflowUI: WorkflowUI, oldState):
        elements = workflowUI.inputElements + workflowUI.outputElements
        keys = [f"{x.element.getKey()}/{workflowUI.name}" for x in elements]
        def getWorkflowUIState(*values):
            if oldState is None:
                stateDict = {"elements": {}}
            else:
                stateDict = oldState._stateDict
            for key, value in zip(keys, values):
                stateDict["elements"][key] = value
            return WorkflowState(stateDict)

        kwargs = dict(
            fn=getWorkflowUIState,
            inputs=[x.gradioComponent for x in elements],
            preprocess=False,
        )
        return kwargs

