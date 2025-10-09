import uuid
import gradio as gr
import os
from mcww.workflow import Workflow
from mcww.workflowUI import WorkflowUI
from mcww.utils import (getStorageKey, getStorageEncryptionKey, ifaceCSS, ifaceCustomHead,
    read_string_from_file, getMcwwLoaderHTML, logoPath, logoHtml, MCWW_WEB_DIR
)
from mcww import opts
from mcww.webUIState import WebUIState, ProjectState
from mcww.processing import Processing

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        self._workflows: dict[str, Workflow] = dict()
        self.webUI = None


    def _refreshWorkflows(self):
        files = os.listdir(opts.COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for file in files:
            if not file.endswith(".json"): continue
            workflowPath = os.path.join(opts.COMFY_WORKFLOWS_PATH, file)
            workflowComfy = read_string_from_file(workflowPath)
            self._workflows[file.removesuffix(".json")]: Workflow = Workflow(workflowComfy)


    def _onRefreshWorkflows(self, selected):
        self._refreshWorkflows()
        choices = list(self._workflows.keys())
        if selected in choices:
            value = selected
        else:
            value= choices[0]
        return gr.Radio(choices=choices, value=value)


    def _initWebUI(self):
        with gr.Blocks(analytics_enabled=False,
                       title=opts.WEBUI_TITLE,
                       theme=opts.GRADIO_THEME,
                       css=ifaceCSS,
                       head=ifaceCustomHead) as self.webUI:
            refreshActiveWorkflowTrigger = gr.Textbox(visible=False)
            refreshActiveWorkflowUIKwargs: dict = dict(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshActiveWorkflowTrigger]
            )
            dummyComponent = gr.Textbox(visible=False)
            def runJSFunctionKwargs(jsFunction: str) -> dict:
                return dict(
                        fn=lambda x: x,
                        inputs=[dummyComponent],
                        outputs=[dummyComponent],
                        js=jsFunction,
                )


            with gr.Sidebar(width=100, open=True):
                gr.HTML(logoHtml, elem_classes=['mcww-logo'])
                hideQueueButton = gr.Button("hide queue")
                showQueueButton = gr.Button("show queue")

                webUIStateComponent = gr.BrowserState(
                    default_value=WebUIState.DEFAULT_WEBUI_STATE_JSON,
                    storage_key=getStorageKey(), secret=getStorageEncryptionKey())
                projectsRadio = gr.Radio(show_label=False, elem_classes=['project-radio'])
                self.webUI.load(
                    fn=WebUIState._onProjectSelected,
                    inputs=[webUIStateComponent],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                )
                projectsRadio.select(
                    **runJSFunctionKwargs("activateLoadingPlaceholder")
                ).then(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=WebUIState._onProjectSelected,
                    inputs=[webUIStateComponent, projectsRadio],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )
                newStateButton = gr.Button("+")
                newStateButton.click(
                    **runJSFunctionKwargs("activateLoadingPlaceholder")
                ).then(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=WebUIState._onNewProjectButtonClicked,
                    inputs=[webUIStateComponent],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )


            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    for _ in range(5):
                        gr.Gallery(interactive=False)
                with gr.Column():
                    gr.HTML(getMcwwLoaderHTML(["startup-loading"]), key=str(uuid.uuid4()))

                    @gr.render(
                        triggers=[refreshActiveWorkflowTrigger.change],
                        inputs=[webUIStateComponent],
                    )
                    def _(webUIState):
                        webUIState = WebUIState(webUIState)
                        activeProjectState: ProjectState = webUIState.getActiveProject()
                        selectedWorkflowName = activeProjectState.getSelectedWorkflow()
                        if selectedWorkflowName not in self._workflows or not self._workflows:
                            self._refreshWorkflows()
                        if selectedWorkflowName not in self._workflows:
                            selectedWorkflowName = list(self._workflows.keys())[0]

                        with gr.Row(equal_height=True):
                            workflowsRadio = gr.Radio(show_label=False, value=selectedWorkflowName,
                                    choices=list[str](self._workflows.keys()))
                            refreshWorkflowsButton = gr.Button("Refresh", scale=0)
                            refreshWorkflowsButton.click(
                                **runJSFunctionKwargs("activateLoadingPlaceholder")
                            ).then(
                                **runJSFunctionKwargs("doSaveStates")
                            ).then(
                                fn=self._onRefreshWorkflows,
                                inputs=[workflowsRadio],
                                outputs=[workflowsRadio]
                            ).then(
                                **refreshActiveWorkflowUIKwargs
                            )
                            workflowsRadio.select(
                                **runJSFunctionKwargs("activateLoadingPlaceholder")
                            ).then(
                                **runJSFunctionKwargs("doSaveStates")
                            ).then(
                                fn=webUIState.onSelectWorkflow,
                                inputs=[workflowsRadio],
                                outputs=[webUIStateComponent],
                            ).then(
                                **refreshActiveWorkflowUIKwargs
                            )

                        workflowUI = WorkflowUI(self._workflows[selectedWorkflowName], selectedWorkflowName)
                        gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                        activeProjectState.setValuesToWorkflowUI(workflowUI)
                        processing = Processing(workflow=workflowUI.workflow,
                                inputElements=[x.element for x in workflowUI.inputElements],
                                outputElements=[x.element for x in workflowUI.outputElements],
                            )
                        workflowUI.runButton.click(
                            **runJSFunctionKwargs("doSaveStates")
                        ).then(
                            fn=processing.onRunButtonClick,
                            inputs=[x.gradioComponent for x in workflowUI.inputElements],
                            outputs=[x.gradioComponent for x in workflowUI.outputElements],
                            postprocess=False,
                            preprocess=False,
                            key=hash(workflowUI.workflow)
                        )

                        saveStatesKwargs = webUIState.getActiveWorkflowStateKwags(workflowUI)
                        saveStateButton = gr.Button(elem_classes=["save-states", "mcww-hidden"])
                        saveStateButton.click(
                            **saveStatesKwargs,
                            outputs=[webUIStateComponent],
                        ).then(
                            **runJSFunctionKwargs("afterStatesSaved")
                        )

            self.webUI.load(
                **refreshActiveWorkflowUIKwargs
            )


    def launch(self):
        allowed_paths = [MCWW_WEB_DIR]
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        self.webUI.launch(allowed_paths=allowed_paths, favicon_path=logoPath)
