from dataclasses import dataclass
import gradio as gr
import json, os, uuid, traceback
from mcww import queueing, opts
from mcww.utils import save_string_to_file, saveLogError, read_string_from_file
from mcww.ui.workflowUI import WorkflowUI
from mcww.ui.webUIState import ProjectState, WebUIState
from mcww.ui.uiUtils import getMcwwLoaderHTML, getRunJSFunctionKwargs, showRenderingErrorGradio
from mcww.comfy.workflowConverting import WorkflowIsNotSupported
from mcww.comfy.workflow import Workflow
from mcww.comfy import comfyAPI


class ProjectUI:
    @dataclass
    class Locals:
        webUIState: WebUIState = None
        activeProjectState: ProjectState = None
        selectedWorkflowName: str = None
        error: Exception|None = None

    def __init__(self, mainUIPageRadio: gr.Radio, webui: gr.Blocks, webUIStateComponent: gr.BrowserState,
                refreshProjectTrigger: gr.Textbox, refreshProjectKwargs: dict):
        self.mainUIPageRadio = mainUIPageRadio
        self.webui = webui
        self.webUIStateComponent = webUIStateComponent
        self.refreshProjectTrigger = refreshProjectTrigger
        self.refreshProjectKwargs = refreshProjectKwargs
        self._workflows: dict[str, Workflow] = dict()
        self._buildProjectUI()


    def _refreshWorkflows(self):
        comfy_workflows_backup_path = os.path.join(opts.STORAGE_DIRECTORY, "comfy_workflows_backup.json")
        self._workflows = dict()
        try:
            comfy_workflows = comfyAPI.getWorkflows()
            comfy_workflows = {key: comfy_workflows[key] for key in
                    sorted([x for x  in comfy_workflows.keys()], key=lambda x: os.path.basename(x).lower())}
            save_string_to_file(json.dumps(comfy_workflows, indent=2), comfy_workflows_backup_path)
        except Exception as e:
            if type(e) == comfyAPI.ComfyIsNotAvailable:
                if os.path.exists(comfy_workflows_backup_path):
                    comfy_workflows = json.loads(read_string_from_file(comfy_workflows_backup_path))
                    gr.Info("Comfy is not available on workflows refresh", 2)
                else:
                    self._workflows = dict()
                    gr.Warning("Comfy is not available on workflows refresh, and no workflows backup", 2)
                    return
            else:
                raise
        for workflow_path, workflow_comfy in comfy_workflows.items():
            try:
                file = os.path.basename(workflow_path)
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


    def _buildProjectUI(self):
        dummyComponent = gr.Textbox(visible=False)
        runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)
        _refreshWorkflowTrigger = gr.Textbox(visible=False)

        with gr.Row(equal_height=True) as projectHead:
            localsComponent = gr.State()
            workflowsRadio = gr.Radio(show_label=False, elem_classes=["workflows-radio"])
            workflowsRadio.select(
                **runJSFunctionKwargs(jsFunctions=[
                    "activateLoadingPlaceholder",
                    "doSaveStates",
                ])
            ).then(
                fn=lambda locals, x: locals.webUIState.onSelectWorkflow(x),
                inputs=[localsComponent, workflowsRadio],
                outputs=[self.webUIStateComponent],
            ).then(
                **self.refreshProjectKwargs
            )

            self.webui.load(**self.refreshProjectKwargs)
            refreshWorkflowsButton = gr.Button("Refresh", scale=0,
                    elem_classes=["mcww-refresh", "mcww-text-button"])
            refreshWorkflowsButton.click(
                **runJSFunctionKwargs([
                    "activateLoadingPlaceholder",
                    "doSaveStates",
                ])
            ).then(
                fn=self._refreshWorkflows,
            ).then(
                **self.refreshProjectKwargs
            )
        gr.HTML(getMcwwLoaderHTML(["startup-loading"]))

        @gr.on(
            triggers=[self.refreshProjectTrigger.change],
            inputs=[localsComponent, self.webUIStateComponent],
            outputs=[localsComponent, _refreshWorkflowTrigger, workflowsRadio],
            show_progress='hidden',
        )
        def _(locals: ProjectUI.Locals|None, webUIStateJson):
            if not locals:
                locals = ProjectUI.Locals()
            locals.error = None
            def nothing():
                return locals, str(uuid.uuid4()), gr.Radio()
            try:
                locals.webUIState = WebUIState(webUIStateJson)
                locals.activeProjectState: ProjectState = locals.webUIState.getActiveProject()

                locals.selectedWorkflowName = locals.activeProjectState.getSelectedWorkflow()
                if locals.selectedWorkflowName not in self._workflows or not self._workflows:
                    self._refreshWorkflows()
                choices = list(self._workflows.keys())
                if not choices:
                    return nothing()
                if locals.selectedWorkflowName not in self._workflows:
                    locals.selectedWorkflowName = choices[0]
                return locals, str(uuid.uuid4()), gr.Radio(value=locals.selectedWorkflowName, choices=choices)
            except Exception as e:
                saveLogError(e)
                e.stack_trace = traceback.format_exc()
                locals.error = e
                return nothing()

        @gr.on(
            triggers=[self.mainUIPageRadio.change],
            inputs=[self.mainUIPageRadio],
            outputs=[projectHead],
            show_progress='hidden',
        )
        def _(mainUIPage: str):
            if mainUIPage != "project":
                return gr.Row(visible=False)
            else:
                return gr.Row(visible=True)

        @gr.render(
            triggers=[_refreshWorkflowTrigger.change, self.mainUIPageRadio.change],
            inputs=[localsComponent, self.mainUIPageRadio],
        )
        def _(locals: ProjectUI.Locals, mainUIPage: str):
            try:
                if mainUIPage != "project": return

                if locals.error:
                    showRenderingErrorGradio(locals.error)
                    return

                if not self._workflows:
                    gr.Markdown("No workflows found. Please ensure that you have workflows "
                        "with proper node titles like `<Prompt:prompt:1>`, `<Image 1:prompt/Image 1:1>`, "
                        "`<Output:output:1>`. Workflow must have at least 1 input node and 1 output node. "
                        "Check the readme for details")
                    return

                workflowUI = WorkflowUI(workflow=self._workflows[locals.selectedWorkflowName],
                        name=locals.selectedWorkflowName, queueMode=False,
                        pullOutputsKey=f"{locals.selectedWorkflowName}-{locals.activeProjectState.getProjectId()}")
                gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                locals.activeProjectState.setValuesToWorkflowUI(workflowUI)
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

                saveStatesKwargs = locals.webUIState.getActiveWorkflowStateKwags(workflowUI)
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

