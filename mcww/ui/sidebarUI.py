import gradio as gr
from mcww.ui.uiUtils import logoHtml, getRunJSFunctionKwargs
from mcww.ui.webUIState import WebUIState


class SidebarUI:
    def __init__(self, webui: gr.Blocks, webUIStateComponent: gr.BrowserState,
                refreshProjectTrigger: gr.Textbox, refreshProjectKwargs: dict):
        self.webui = webui
        self.webUIStateComponent = webUIStateComponent
        self.refreshActiveWorkflowTrigger = refreshProjectTrigger
        self.refreshProjectKwargs = refreshProjectKwargs
        self._buildSidebarUI()


    def _buildSidebarUI(self):
        dummyComponent = gr.Textbox(visible=False)
        runJSFunctionKwargs = getRunJSFunctionKwargs(dummyComponent)

        gr.HTML(logoHtml, elem_classes=['mcww-logo'])
        self.mainUIPageRadio = gr.Radio(show_label=False, elem_classes=["mcww-main-ui-page", "mcww-hidden"],
            choices=["project", "queue", "helpers", "settings", "wolf3d"], value="project")
        toggleQueue = gr.Button(" Queue", elem_classes=["mcww-glass", "mcww-queue"])
        toggleQueue.click(
            **runJSFunctionKwargs([
                "closeSidebarOnMobile",
                "doSaveStates",
                "onQueueButtonPressed",
            ])
        )

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
            inputs=[self.webUIStateComponent, projectsRadio],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
        )

        closeProjectsRadio = gr.Radio(show_label=False, elem_classes=['close-projects-radio', 'mcww-hidden'])
        closeProjectsRadio.select(
            **runJSFunctionKwargs("doSaveStates")
        ).then(
            fn=WebUIState.onProjectClosed,
            inputs=[self.webUIStateComponent, closeProjectsRadio],
            outputs=[self.webUIStateComponent, projectsRadio, closeProjectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
        )

        projectsRadio.change(
            fn=WebUIState.onGetCloseProjectsRadio,
            inputs=[self.webUIStateComponent],
            outputs=[closeProjectsRadio],
        )

        self.webui.load(
            fn=WebUIState.onProjectSelected,
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
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
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
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
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
        )

        with gr.Group(elem_classes=["mcww-bottom-buttons"]):
            helpersButton = gr.Button("Helpers",
                elem_classes=["mcww-text-button", "mcww-helpers-button"])
            helpersButton.click(
                **runJSFunctionKwargs([
                    "closeSidebarOnMobile",
                    "doSaveStates",
                    "onHelpersButtonPressed",
                ])
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


