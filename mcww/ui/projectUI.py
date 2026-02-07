from dataclasses import dataclass
import gradio as gr
import json, os, uuid
from mcww import queueing, opts, shared
from mcww.utils import save_string_to_file, saveLogError, read_string_from_file
from mcww.ui.workflowUI import WorkflowUI
from mcww.ui.webUIState import ProjectState, WebUIState
from mcww.ui.uiUtils import getMcwwLoaderHTML, showRenderingErrorGradio
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

    def __init__(self, webUIStateComponent: gr.BrowserState, refreshProjectTrigger: gr.Textbox, refreshProjectKwargs: dict):
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
                    comfy_workflows = dict()
                    gr.Warning("Comfy is not available on workflows refresh, and no workflows backup", 2)
            else:
                raise

        shared.workflowsLoadingContext.clear()

        for workflow_path, workflow_comfy in comfy_workflows.items():
            file = os.path.basename(workflow_path)
            base_workflow_name = os.path.splitext(file)[0]
            workflow_name = base_workflow_name

            counter = 0
            while workflow_name in self._workflows:
                counter += 1
                workflow_name = f"{base_workflow_name} ({counter})"

            try:
                with shared.workflowsLoadingContext(f'Warning parsing workflow "{workflow_path}"'):
                    workflow = Workflow(workflow_comfy)
            except Exception as e:
                with shared.workflowsLoadingContext(f'Rejected workflow "{workflow_path}"'):
                    if isinstance(e, WorkflowIsNotSupported):
                        shared.workflowsLoadingContext.warning(f"Workflow is not supported: {e}")
                    else:
                        textCopy = saveLogError(e, prefixTitleLine=f"Error loading workflow {file}")
                        shared.workflowsLoadingContext.warning(textCopy)
            else:
                if workflow.isValid():
                    self._workflows[workflow_name] = workflow
                else:
                    with shared.workflowsLoadingContext("Workflows missing mandatory categories"):
                        shared.workflowsLoadingContext.warning(workflow_path)
        return gr.Radio()


    def _buildProjectUI(self):
        _refreshWorkflowTrigger = gr.Textbox(visible=False)

        with gr.Column() as self.ui:
            with gr.Row(equal_height=True):
                localsComponent = gr.State()
                workflowsRadio = gr.Radio(show_label=False, elem_classes=["workflows-radio", "scroll-to-selected"])
                workflowsRadio.select(
                    **shared.runJSFunctionKwargs([
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
                workflowsRadio.change(
                    **shared.runJSFunctionKwargs([
                        "scrollSelectedOnChange",
                        "updateSelectedWorkflowTitle",
                    ])
                )

                shared.webUI.load(**self.refreshProjectKwargs)
                refreshWorkflowsButton = gr.Button("Refresh", scale=0,
                        elem_classes=["mcww-refresh", "mcww-text-button"])
                refreshWorkflowsButton.click(
                    **shared.runJSFunctionKwargs([
                        "activateLoadingPlaceholder",
                        "doSaveStates",
                    ])
                ).then(
                    fn=self._refreshWorkflows,
                    outputs=[workflowsRadio],
                ).then(
                    **self.refreshProjectKwargs
                )

            @gr.on(
                triggers=[self.refreshProjectTrigger.change],
                inputs=[localsComponent, self.webUIStateComponent],
                outputs=[localsComponent, _refreshWorkflowTrigger, workflowsRadio],
                show_progress='hidden',
            )
            def onRefreshProject(locals: ProjectUI.Locals|None, webUIStateJson):
                if not locals:
                    locals = ProjectUI.Locals()
                locals.error = None
                def nothing():
                    return locals, str(uuid.uuid4()), gr.Radio()
                try:
                    locals.webUIState = WebUIState(webUIStateJson)
                    locals.activeProjectState: ProjectState = locals.webUIState.getActiveProject()

                    locals.selectedWorkflowName = locals.activeProjectState.getSelectedWorkflow()
                    if not self._workflows:
                        self._refreshWorkflows()
                    choices = list(self._workflows.keys())
                    if not choices:
                        return nothing()
                    if locals.selectedWorkflowName not in self._workflows:
                        locals.selectedWorkflowName = choices[0]
                    return locals, str(uuid.uuid4()), gr.Radio(value=locals.selectedWorkflowName, choices=choices)
                except Exception as e:
                    saveLogError(e, "Error on refresh workflows")
                    locals.error = e
                    return nothing()

            @gr.render(
                triggers=[_refreshWorkflowTrigger.change],
                inputs=[localsComponent],
            )
            def renderProjectWorkflow(locals: ProjectUI.Locals|None):
                try:
                    if not locals:
                        gr.Markdown("Locals are None in renderProjectWorkflow", elem_classes=["mcww-visible"])
                        return
                    if locals.error:
                        showRenderingErrorGradio(locals.error, "Error on refresh workflows")
                        return

                    if not self._workflows:
                        gr.Markdown("No workflows found. Please ensure that you have workflows "
                            "with proper node titles like `<Prompt:prompt:1>`, `<Image 1:prompt/Image 1:1>`, "
                            "`<Output:output:1>`. Workflow must have at least 1 input node and 1 output node. "
                            "Check the readme for details", elem_classes=["mcww-visible"])
                        return

                    with gr.Column(elem_classes=['project-workflow-ui']):
                        workflowUI = WorkflowUI(workflow=self._workflows[locals.selectedWorkflowName],
                            name=locals.selectedWorkflowName, mode=WorkflowUI.Mode.PROJECT,
                            pullOutputsKey=f"{locals.selectedWorkflowName}-{locals.activeProjectState.getProjectId()}")
                    gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                    locals.activeProjectState.setValuesToWorkflowUI(workflowUI)

                    runButton = gr.Button("Run", elem_classes=['mcww-run-button'], variant='primary')
                    runButton.click(
                        **shared.runJSFunctionKwargs("doSaveStates")
                    ).then(
                        fn=queueing.queue.getOnRunButtonClicked(
                            workflow=workflowUI.workflow,
                            workflowName=workflowUI.name,
                            inputElements=[x.element for x in workflowUI.inputElements],
                            outputElements=[x.element for x in workflowUI.outputElements],
                            mediaSingleElements=[x.element for x in workflowUI.mediaSingleElements],
                            mediaBatchElements=[x.element for x in workflowUI.mediaBatchElements],
                            pullOutputsKey=workflowUI.pullOutputsKey,
                        ),
                        inputs=[x.gradioComponent for x in
                                      workflowUI.inputElements
                                    + workflowUI.mediaSingleElements
                                    + workflowUI.mediaBatchElements]
                                + [workflowUI.selectedMediaTabComponent],
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
                        **shared.runJSFunctionKwargs("afterStatesSaved")
                    )

                    pullOutputsButton = gr.Button(json.dumps({
                                "type": "outputs",
                                "outputs_key": workflowUI.pullOutputsKey,
                                "oldVersion": None,
                            }),
                            elem_classes=["mcww-pull", "mcww-hidden"])
                    pullOutputsButton.click(
                        fn=queueing.queue.getOnPullOutputs(
                            outputElementsUI=workflowUI.outputElements,
                            pullOutputsKey=workflowUI.pullOutputsKey,
                        ),
                        inputs=[],
                        outputs=[x.gradioComponent for x in workflowUI.outputElements]
                            + [workflowUI.outputRunningHtml, workflowUI.outputErrorMarkdown],
                        postprocess=False,
                        preprocess=False,
                        show_progress="hidden",
                    ).then(
                        **shared.runJSFunctionKwargs("pullIsDone")
                    )

                except Exception as e:
                    showRenderingErrorGradio(e, "Error on rendering project workflow")

            initLoader = gr.HTML(getMcwwLoaderHTML())
            hideInitLoader = gr.Button(elem_classes=["mcww-hidden", "hide-init-workflow-loader"])
            hideInitLoader.click(
                fn=lambda: gr.update(visible=False),
                outputs=[initLoader],
            )

