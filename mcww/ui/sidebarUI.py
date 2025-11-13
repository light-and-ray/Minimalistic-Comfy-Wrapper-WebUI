import gradio as gr
from mcww import shared
from mcww.ui.uiUtils import logoHtml, MAIN_UI_PAGES
from mcww.ui.webUIState import WebUIState


class SidebarUI:
    def __init__(self, webUIStateComponent: gr.BrowserState,
                refreshProjectTrigger: gr.Textbox, refreshProjectKwargs: dict):
        self.webUIStateComponent = webUIStateComponent
        self.refreshActiveWorkflowTrigger = refreshProjectTrigger
        self.refreshProjectKwargs = refreshProjectKwargs
        self._buildSidebarUI()


    def _buildSidebarUI(self):
        gr.HTML(logoHtml, elem_classes=['mcww-logo'])
        self.mainUIPageRadio = gr.Radio(show_label=False, elem_classes=["mcww-main-ui-page", "mcww-hidden"],
            choices=MAIN_UI_PAGES, value="project")
        toggleQueue = gr.Button(" Queue", elem_classes=["mcww-glass", "mcww-queue"])
        toggleQueue.click(
            **shared.runJSFunctionKwargs([
                "doSaveStates",
                "onQueueButtonPressed",
                "closeSidebarOnMobile",
            ])
        )

        projectsRadio = gr.Radio(show_label=False, elem_classes=['projects-radio'])
        projectsRadio.select(
            **shared.runJSFunctionKwargs([
                "activateLoadingPlaceholder",
                "doSaveStates"
                "ensureProjectIsSelected",
                "closeSidebarOnMobile",
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
            **shared.runJSFunctionKwargs("doSaveStates")
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

        shared.webUI.load(
            fn=WebUIState.onProjectSelected,
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        )

        newStateButton = gr.Button("＋ New", elem_classes=["mcww-glass"])
        newStateButton.click(
            **shared.runJSFunctionKwargs([
                "activateLoadingPlaceholder",
                "doSaveStates"
            ])
        ).then(
            fn=WebUIState.onNewProjectButtonClicked,
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
        ).then(
            **shared.runJSFunctionKwargs([
                "ensureProjectIsSelected",
                "closeSidebarOnMobile",
            ])
        )

        copyButton = gr.Button("⎘ Copy", elem_classes=["mcww-glass"])
        copyButton.click(
            **shared.runJSFunctionKwargs([
                "activateLoadingPlaceholder",
                "doSaveStates"
            ])
        ).then(
            fn=WebUIState.onCopyProjectButtonClicked,
            inputs=[self.webUIStateComponent],
            outputs=[self.webUIStateComponent, projectsRadio],
            show_progress="hidden",
        ).then(
            **self.refreshProjectKwargs
        ).then(
            **shared.runJSFunctionKwargs([
                "ensureProjectIsSelected",
                "closeSidebarOnMobile",
            ])
        )

        with gr.Group(elem_classes=["mcww-bottom-buttons"]):
            helpersButton = gr.Button("Helpers",
                elem_classes=["mcww-text-button", "mcww-helpers-button"])
            helpersButton.click(
                **shared.runJSFunctionKwargs([
                    "doSaveStates",
                    "onHelpersButtonPressed",
                    "closeSidebarOnMobile",
                ])
            )

            optionsButton = gr.Button("Options",
                elem_classes=["mcww-text-button", "mcww-options-button"])
            optionsButton.click(
                **shared.runJSFunctionKwargs([
                    "doSaveStates",
                    "onOptionsButtonPressed",
                    "closeSidebarOnMobile",
                ])
            )

            compareButton = gr.Button("Compare",
                elem_classes=["mcww-hidden"])
            compareButton.click(
                **shared.runJSFunctionKwargs([
                    "doSaveStates",
                    "openComparePage",
                ])
            )


