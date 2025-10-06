import uuid
import gradio as gr
import os
from mcww.workflow import Workflow
from mcww.workflowUI import WorkflowUI
from mcww.utils import ifaceCSS, ifaceCustomHead, read_string_from_file
from mcww import opts
from mcww.workflowState import WorkflowState, WorkflowStates

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        self._workflows: dict[str, Workflow] = dict()
        self.webUI = None


    def _onRefreshWorkflows(self, selected):
        files = os.listdir(opts.COMFY_WORKFLOWS_PATH)
        self._workflows: dict[str, Workflow] = dict()
        for file in files:
            if not file.endswith(".json"): continue
            workflowPath = os.path.join(opts.COMFY_WORKFLOWS_PATH, file)
            workflowComfy = read_string_from_file(workflowPath)
            self._workflows[file.removesuffix(".json")]: Workflow = Workflow(workflowComfy)
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
            with gr.Sidebar(width=100, open=False):
                hideQueueButton = gr.Button("hide queue")
                showQueueButton = gr.Button("show queue")
                openedStates = gr.State()
                @gr.render(
                    triggers=[openedStates.change, self.webUI.load],
                    inputs=[openedStates]
                )
                def _(states: WorkflowStates|None):
                    if not states:
                        states = WorkflowStates()
                    states.render(openedStates)


            with gr.Row(equal_height=True):
                workflowsRadio = gr.Radio(show_label=False)
                refreshWorkflowsButton = gr.Button("Refresh", scale=0)
                refreshWorkflowTrigger = gr.Textbox(visible=False)
                refreshWorkflowUIKwargs = dict(
                    fn=lambda: str(uuid.uuid4()),
                    outputs=[refreshWorkflowTrigger]
                )
            with gr.Row():
                with gr.Column(visible=False) as queueColumn:
                    for _ in range(5):
                        gr.Gallery(interactive=False)
                with gr.Column():
                    @gr.render(
                        triggers=[refreshWorkflowTrigger.change],
                        inputs=[workflowsRadio, openedStates],
                    )
                    def _(name, states: WorkflowStates|None):
                        # saveStateButton = gr.Button("Save state")
                        if not states:
                            states = WorkflowStates()
                        workflowUI = WorkflowUI(self._workflows[name], name)
                        workflowUIStateKwargs = WorkflowState.getWorkflowUIStateKwargs(workflowUI, states)
                        workflowsRadio.change(
                            **workflowUIStateKwargs,
                            outputs=[openedStates],
                        ).then(**refreshWorkflowUIKwargs)
                        states.getSelectedWorkflowState().setValuesToWorkflowUI(workflowUI)


            refreshWorkflowsKwargs = dict(
                fn=self._onRefreshWorkflows,
                inputs=[workflowsRadio],
                outputs=[workflowsRadio]
            )

            self.webUI.load(
                **refreshWorkflowsKwargs
            ).then(**refreshWorkflowUIKwargs)

            refreshWorkflowsButton.click(
                **refreshWorkflowsKwargs
            ).then(**refreshWorkflowUIKwargs)

            openedStates.change(
                **refreshWorkflowsKwargs
            ).then(**refreshWorkflowUIKwargs)


    def launch(self):
        allowed_paths = []
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        self.webUI.launch(allowed_paths=allowed_paths)
