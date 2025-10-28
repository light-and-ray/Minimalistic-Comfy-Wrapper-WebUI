import gradio as gr
from mcww import queueing
from mcww.workflowUI import WorkflowUI
import json, os, uuid
from mcww.webUIState import ProjectState
from mcww.utils import (getMcwwLoaderHTML, getRunJSFunctionKwargs, saveLogError,
    showRenderingErrorGradio, read_string_from_file
)
from mcww.webUIState import WebUIState
from mcww.workflowConverting import WorkflowIsNotSupported
from mcww import opts
from mcww.workflow import Workflow



class ProjectUI:
    def __init__(self, mainUIPageRadio: gr.Radio, webui: gr.Blocks, webUIStateComponent: gr.BrowserState,
                refreshProjectTrigger: gr.Textbox, refreshProjectKwargs: dict):
        self.mainUIPageRadio = mainUIPageRadio
        self.webui = webui
        self.webUIStateComponent = webUIStateComponent
        self.refreshProjectTrigger = refreshProjectTrigger
        self.refreshProjectKwargs = refreshProjectKwargs
        self._workflows: dict[str, Workflow] = dict()
        self.webUIState: WebUIState = None
        self.activeProjectState: ProjectState = None
        self.selectedWorkflowName: str = None
        self._buildProjectUI()


    def _refreshWorkflows(self):
        self._workflows = dict()
        for root, _, files in os.walk(opts.COMFY_WORKFLOWS_PATH):
            for file in files:
                if not file.endswith(".json"):
                    continue
                if file == ".index.json":
                    continue
                workflow_path = os.path.join(root, file)
                try:
                    workflow_comfy = read_string_from_file(workflow_path)

                    base_workflow_name = os.path.splitext(file)[0]
                    workflow_name = base_workflow_name

                    counter = 0
                    while workflow_name in self._workflows:
                        counter += 1
                        workflow_name = f"{base_workflow_name} ({counter})"

                    workflow = Workflow(workflow_comfy)
                    if workflow.isValid():
                        self._workflows[workflow_name] = workflow
                except Exception as e:
                    if isinstance(e, WorkflowIsNotSupported):
                        print(f"Workflow is not supported '{file}': {e}")
                    else:
                        saveLogError(e, prefixTitleLine=f"Error loading workflow {file}")
                continue


    def _onRefreshWorkflows(self, selected):
        self._refreshWorkflows()
        choices = list(self._workflows.keys())
        if selected in choices:
            value = selected
        else:
            value= choices[0]
        return gr.Radio(choices=choices, value=value), str(uuid.uuid4())


    def _buildProjectUI(self):
        dummyComponent = gr.Textbox(visible=False)
        runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)
        refreshRadioTrigger = gr.Textbox(visible=False)
        _refreshWorkflowTrigger = gr.Textbox(visible=False)

        with gr.Row(equal_height=True):
            workflowsRadio = gr.Radio(show_label=False, elem_classes=["workflows-radio"])
            workflowsRadio.select(
                **runJSFunctionKwargs(jsFunctions=[
                    "activateLoadingPlaceholder",
                    "doSaveStates",
                ])
            ).then(
                fn=lambda x: self.webUIState.onSelectWorkflow(x),
                inputs=[workflowsRadio],
                outputs=[self.webUIStateComponent],
            ).then(
                **self.refreshProjectKwargs
            )


            self.webui.load(fn=lambda: str(uuid.uuid4()), outputs=[refreshRadioTrigger])
            refreshWorkflowsButton = gr.Button("Refresh", scale=0,
                    elem_classes=["mcww-refresh", "mcww-text-button"])
            refreshWorkflowsButton.click(
                **runJSFunctionKwargs([
                    "activateLoadingPlaceholder",
                    "doSaveStates",
                ])
            ).then(
                fn=lambda: str(uuid.uuid4()), outputs=[refreshRadioTrigger]
            )

            refreshRadioTrigger.change(
                fn=self._onRefreshWorkflows,
                inputs=[workflowsRadio],
                outputs=[workflowsRadio, self.refreshProjectTrigger]
            )
        gr.HTML(getMcwwLoaderHTML(["startup-loading"]))

        @gr.on(
            triggers=[self.refreshProjectTrigger.change],
            inputs=[self.webUIStateComponent],
            outputs=[_refreshWorkflowTrigger],
            show_progress=False,
        )
        def _(webUIStateJson):
            self.webUIState = WebUIState(webUIStateJson)
            self.activeProjectState: ProjectState = self.webUIState.getActiveProject()

            self.selectedWorkflowName = self.activeProjectState.getSelectedWorkflow()
            if self.selectedWorkflowName not in self._workflows or not self._workflows:
                self._refreshWorkflows()
            if not self._workflows:
                gr.Markdown("No workflows found. Please ensure that you have workflows "
                    "with proper node titles like `<Prompt:prompt:1>`, `<Image 1:prompt/Image 1:1>`, "
                    "`<Output:output:1>`. Workflow must have at least 1 input node and 1 output node. "
                    "Check the readme for details")
                return
            if self.selectedWorkflowName not in self._workflows:
                self.selectedWorkflowName = list(self._workflows.keys())[0]
            return str(uuid.uuid4())

        @gr.on(
            triggers=[self.mainUIPageRadio.change],
            inputs=[self.mainUIPageRadio],
            outputs=[workflowsRadio],
            show_progress=False,
        )
        def _(mainUIPage: str):
            if  mainUIPage != "project":
                return gr.Radio(visible=False)
            else:
                return gr.Radio(visible=True)

        @gr.render(
            triggers=[_refreshWorkflowTrigger.change, self.mainUIPageRadio.change],
            inputs=[self.mainUIPageRadio],
        )
        def _(mainUIPage: str):
            try:
                if  mainUIPage != "project": return

                workflowUI = WorkflowUI(workflow=self._workflows[self.selectedWorkflowName],
                        name=self.selectedWorkflowName, queueMode=False,
                        pullOutputsKey=f"{self.selectedWorkflowName}-{self.activeProjectState.getProjectId()}")
                gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                self.activeProjectState.setValuesToWorkflowUI(workflowUI)
                workflowUI.runButton.click(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=queueing.queue.getOnRunButtonClicked(workflow=workflowUI.workflow,
                        inputElements=[x.element for x in workflowUI.inputElements],
                        outputElements=[x.element for x in workflowUI.outputElements],
                        pullOutputsKey=workflowUI.pullOutputsKey,
                    ),
                    inputs=[x.gradioComponent for x in workflowUI.inputElements],
                    outputs=[],
                    postprocess=False,
                    preprocess=False,
                )

                saveStatesKwargs = self.webUIState.getActiveWorkflowStateKwags(workflowUI)
                saveStateButton = gr.Button(elem_classes=["save-states", "mcww-hidden"])
                saveStateButton.click(
                    **saveStatesKwargs,
                    outputs=[self.webUIStateComponent],
                ).then(
                    **runJSFunctionKwargs("afterStatesSaved")
                )

                pullOutputsButton = gr.Button(json.dumps({
                            "type": "outputs",
                            "outputs_key": workflowUI.pullOutputsKey,
                            "oldVersion": None,
                        }),
                        elem_classes=["mcww-pull", "mcww-hidden"])
                pullOutputsButton.click(
                    fn=queueing.queue.getOnPullOutputs(
                        outputComponents=[x.gradioComponent for x in workflowUI.outputElements],
                        pullOutputsKey=workflowUI.pullOutputsKey,
                    ),
                    inputs=[],
                    outputs=[x.gradioComponent for x in workflowUI.outputElements],
                    postprocess=False,
                    preprocess=False,
                    show_progress="hidden",
                )

            except Exception as e:
                saveLogError(e)
                showRenderingErrorGradio(e)

