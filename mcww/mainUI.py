import uuid
import gradio as gr
import os
from mcww.workflow import Workflow
from mcww.workflowUI import WorkflowUI
from mcww.utils import (getStorageKey, getStorageEncryptionKey, ifaceCSS, getIfaceCustomHead,
    read_string_from_file, getMcwwLoaderHTML, logoPath, logoHtml, MCWW_WEB_DIR,
    applyConsoleFilters, getRunJSFunctionKwargs
)
from mcww import opts
from mcww.webUIState import WebUIState, ProjectState
from mcww import queueing
from mcww.queueUI import QueueUI

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
                       head=getIfaceCustomHead()) as self.webUI:
            refreshActiveWorkflowTrigger = gr.Textbox(visible=False)
            refreshActiveWorkflowUIKwargs: dict = dict(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshActiveWorkflowTrigger]
            )
            dummyComponent = gr.Textbox(visible=False)
            runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)


            with gr.Sidebar(width=100, open=True):
                gr.HTML(logoHtml, elem_classes=['mcww-logo'])
                mainUIPageRadio = gr.Radio(show_label=False, elem_classes=["mcww-main-ui-page", "mcww-hidden"],
                    choices=["project", "queue", "settings", "wolf3d"], value="project")
                toggleQueue = gr.Button(" Queue", elem_classes=["mcww-glass", "mcww-queue"])
                toggleQueue.click(
                    **runJSFunctionKwargs([
                        "closeSidebarOnMobile",
                        "doSaveStates",
                        "onQueueButtonPressed",
                    ])
                )

                webUIStateComponent = gr.BrowserState(
                    default_value=WebUIState.DEFAULT_WEBUI_STATE_JSON,
                    storage_key=getStorageKey(), secret=getStorageEncryptionKey())
                projectsRadio = gr.Radio(show_label=False, elem_classes=['projects-radio'])
                projectsRadio.select(
                    **runJSFunctionKwargs([
                        "closeSidebarOnMobile",
                        "activateLoadingPlaceholder",
                        "ensureProjectIsSelected",
                        "doSaveStates"
                    ])
                ).then(
                    fn=WebUIState.onProjectSelected,
                    inputs=[webUIStateComponent, projectsRadio],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )

                closeProjectsRadio = gr.Radio(show_label=False, elem_classes=['close-projects-radio', 'mcww-hidden'])
                closeProjectsRadio.select(
                    **runJSFunctionKwargs("doSaveStates")
                ).then(
                    fn=WebUIState.onProjectClosed,
                    inputs=[webUIStateComponent, closeProjectsRadio],
                    outputs=[webUIStateComponent, projectsRadio, closeProjectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )

                projectsRadio.change(
                    fn=WebUIState.onGetCloseProjectsRadio,
                    inputs=[webUIStateComponent],
                    outputs=[closeProjectsRadio],
                )

                self.webUI.load(
                    fn=WebUIState.onProjectSelected,
                    inputs=[webUIStateComponent],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                )

                newStateButton = gr.Button("＋ New", elem_classes=["mcww-glass"])
                newStateButton.click(
                    **runJSFunctionKwargs([
                        "closeSidebarOnMobile",
                        "activateLoadingPlaceholder",
                        "ensureProjectIsSelected",
                        "doSaveStates"
                    ])
                ).then(
                    fn=WebUIState.onNewProjectButtonClicked,
                    inputs=[webUIStateComponent],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )

                copyButton = gr.Button("⎘ Copy", elem_classes=["mcww-glass"])
                copyButton.click(
                    **runJSFunctionKwargs([
                        "closeSidebarOnMobile",
                        "activateLoadingPlaceholder",
                        "ensureProjectIsSelected",
                        "doSaveStates"
                    ])
                ).then(
                    fn=WebUIState.onCopyProjectButtonClicked,
                    inputs=[webUIStateComponent],
                    outputs=[webUIStateComponent, projectsRadio],
                    show_progress="hidden",
                ).then(
                    **refreshActiveWorkflowUIKwargs
                )

                settingsButton = gr.Button("Settings",
                    elem_classes=["mcww-text-button", "mcww-settings-button"])
                settingsButton.click(
                    **runJSFunctionKwargs([
                        "closeSidebarOnMobile",
                        "doSaveStates",
                        "onSettingsButtonPressed",
                    ])
                )

            gr.HTML(getMcwwLoaderHTML(["startup-loading"]))


            QueueUI(mainUIPageRadio, self.webUI)

            @gr.render(
                triggers=[refreshActiveWorkflowTrigger.change, mainUIPageRadio.change],
                inputs=[webUIStateComponent, mainUIPageRadio],
            )
            def _(webUIState, mainUIPage: str):
                webUIState = WebUIState(webUIState)

                if  mainUIPage == "project":
                    activeProjectState: ProjectState = webUIState.getActiveProject()
                    selectedWorkflowName = activeProjectState.getSelectedWorkflow()
                    if selectedWorkflowName not in self._workflows or not self._workflows:
                        self._refreshWorkflows()
                    if selectedWorkflowName not in self._workflows:
                        selectedWorkflowName = list(self._workflows.keys())[0]

                    with gr.Row(equal_height=True):
                        workflowsRadio = gr.Radio(show_label=False, value=selectedWorkflowName,
                                choices=list[str](self._workflows.keys()))
                        refreshWorkflowsButton = gr.Button("Refresh", scale=0,
                                elem_classes=["mcww-refresh", "mcww-text-button"])
                        refreshWorkflowsButton.click(
                            **runJSFunctionKwargs([
                                "activateLoadingPlaceholder",
                                "doSaveStates",
                            ])
                        ).then(
                            fn=self._onRefreshWorkflows,
                            inputs=[workflowsRadio],
                            outputs=[workflowsRadio]
                        ).then(
                            **refreshActiveWorkflowUIKwargs
                        )
                        workflowsRadio.select(
                            **runJSFunctionKwargs([
                                "activateLoadingPlaceholder",
                                "doSaveStates",
                            ])
                        ).then(
                            fn=webUIState.onSelectWorkflow,
                            inputs=[workflowsRadio],
                            outputs=[webUIStateComponent],
                        ).then(
                            **refreshActiveWorkflowUIKwargs
                        )

                    workflowUI = WorkflowUI(workflow=self._workflows[selectedWorkflowName],
                            name=selectedWorkflowName, needResizableRow=True)
                    gr.HTML(getMcwwLoaderHTML(["workflow-loading-placeholder", "mcww-hidden"]))
                    activeProjectState.setValuesToWorkflowUI(workflowUI)
                    pullOutputsKey = f"{workflowUI.name}/{activeProjectState.getProjectId()}"
                    workflowUI.runButton.click(
                        **runJSFunctionKwargs("doSaveStates")
                    ).then(
                        fn=queueing.queue.getOnRunButtonClicked(workflow=workflowUI.workflow,
                            inputElements=[x.element for x in workflowUI.inputElements],
                            outputElements=[x.element for x in workflowUI.outputElements],
                            pullOutputsKey=pullOutputsKey,
                        ),
                        inputs=[x.gradioComponent for x in workflowUI.inputElements],
                        outputs=[],
                        postprocess=False,
                        preprocess=False,
                    )

                    saveStatesKwargs = webUIState.getActiveWorkflowStateKwags(workflowUI)
                    saveStateButton = gr.Button(elem_classes=["save-states", "mcww-hidden"])
                    saveStateButton.click(
                        **saveStatesKwargs,
                        outputs=[webUIStateComponent],
                    ).then(
                        **runJSFunctionKwargs("afterStatesSaved")
                    )

                    pullOutputsButton = gr.Button("Pull outputs",
                            elem_classes=["mcww-pull", "mcww-hidden"])
                    pullOutputsButton.click(
                        fn=queueing.queue.getOnPullOutputs(
                            outputComponents=[x.gradioComponent for x in workflowUI.outputElements],
                            pullOutputsKey=pullOutputsKey,
                        ),
                        inputs=[],
                        outputs=[x.gradioComponent for x in workflowUI.outputElements],
                        postprocess=False,
                        preprocess=False,
                        show_progress="hidden",
                    )

                elif mainUIPage == "settings":
                    gr.Markdown("Settings will be here")
                elif mainUIPage == "wolf3d":
                    gr.HTML(opts.easterEggWolf3dIframe)

            self.webUI.load(
                **refreshActiveWorkflowUIKwargs
            )


    def launch(self):
        allowed_paths = [MCWW_WEB_DIR]
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        applyConsoleFilters()
        self.webUI.launch(allowed_paths=allowed_paths, favicon_path=logoPath)
