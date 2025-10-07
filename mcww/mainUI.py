import uuid
import gradio as gr
import os
from mcww.workflow import Workflow
from mcww.workflowUI import WorkflowUI
from mcww.utils import getStorageKey, ifaceCSS, ifaceCustomHead, read_string_from_file
from mcww import opts
from mcww.workflowState import WorkflowStates ,WorkflowState
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

            with gr.Sidebar(width=100, open=False):
                hideQueueButton = gr.Button("hide queue")
                showQueueButton = gr.Button("show queue")
                openedStates = gr.BrowserState(
                    default_value=WorkflowStates.DEFAULT_STATES_JSON,
                    storage_key=getStorageKey(), secret=1)
                statesRadio = gr.Radio(show_label=False)
                self.webUI.load(
                    fn=WorkflowStates._onSelected,
                    inputs=[openedStates],
                    outputs=[openedStates, statesRadio],
                    show_progress="hidden",
                )
                statesRadio.select(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=WorkflowStates._onSelected,
                    inputs=[openedStates, statesRadio],
                    outputs=[openedStates, statesRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )
                newStateButton = gr.Button("+")
                newStateButton.click(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=WorkflowStates._onNewButtonClicked,
                    inputs=[openedStates],
                    outputs=[openedStates, statesRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )


            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    for _ in range(5):
                        gr.Gallery(interactive=False)
                with gr.Column():
                    @gr.render(
                        triggers=[refreshActiveWorkflowTrigger.change],
                        inputs=[openedStates],
                    )
                    def _(states):
                        states = WorkflowStates(states)
                        activeState: WorkflowState = states.getSelectedState()
                        selectedWorkflowName = activeState.getSelectedWorkflow()
                        if selectedWorkflowName not in self._workflows or not self._workflows:
                            self._refreshWorkflows()
                        if selectedWorkflowName not in self._workflows:
                            selectedWorkflowName = list(self._workflows.keys())[0]

                        with gr.Row(equal_height=True):
                            workflowsRadio = gr.Radio(show_label=False, value=selectedWorkflowName,
                                    choices=list[str](self._workflows.keys()))
                            refreshWorkflowsButton = gr.Button("Refresh", scale=0)
                            refreshWorkflowsButton.click(
                                **runJSFunctionKwargs("doSaveStates")
                            ).then(
                                fn=self._onRefreshWorkflows,
                                inputs=[workflowsRadio],
                                outputs=[workflowsRadio]
                            ).then(
                                **refreshActiveWorkflowUIKwargs
                            )
                            workflowsRadio.select(
                                **runJSFunctionKwargs("doSaveStates")
                            ).then(
                                fn=states.onSelectWorkflow,
                                inputs=[workflowsRadio],
                                outputs=[openedStates],
                            ).then(
                                **refreshActiveWorkflowUIKwargs
                            )

                        workflowUI = WorkflowUI(self._workflows[selectedWorkflowName], selectedWorkflowName)
                        activeState.setValuesToWorkflowUI(workflowUI)
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

                        saveStatesKwargs = states.getSaveStatesKwargs(workflowUI)
                        saveStateButton = gr.Button(elem_classes=["save_states"])
                        saveStateButton.click(
                            **saveStatesKwargs,
                            outputs=[openedStates],
                        ).then(
                            **runJSFunctionKwargs("afterStatesSaved")
                        )
            self.webUI.load(
                **refreshActiveWorkflowUIKwargs
            )


    def launch(self):
        allowed_paths = []
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        self.webUI.launch(allowed_paths=allowed_paths)
