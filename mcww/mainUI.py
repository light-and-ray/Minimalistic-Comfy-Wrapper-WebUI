from mcww.mcwwAPI import API
import gradio as gr
import os, time, uuid
from mcww.utils import (getStorageKey, getStorageEncryptionKey, ifaceCSS, getIfaceCustomHead,
    getMcwwLoaderHTML, logoPath, logoHtml, MCWW_WEB_DIR, applyConsoleFilters,
    getRunJSFunctionKwargs, saveLogError, showRenderingErrorGradio
)
from mcww import opts
from mcww.webUIState import WebUIState
from mcww.queueUI import QueueUI
from mcww.projectUI import ProjectUI
from mcww.mcwwAPI import API

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        self.webUI = None


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

            ProjectUI(mainUIPageRadio, self.webUI, webUIStateComponent,
                        refreshActiveWorkflowTrigger, refreshActiveWorkflowUIKwargs)

            @gr.render(
                triggers=[mainUIPageRadio.change],
                inputs=[mainUIPageRadio],
            )
            def _(mainUIPage: str):
                try:
                    if mainUIPage == "settings":
                        gr.Markdown("Settings will be here")
                    elif mainUIPage == "wolf3d":
                        gr.HTML(opts.easterEggWolf3dIframe)
                except Exception as e:
                    saveLogError(e)
                    showRenderingErrorGradio(e)


    def launch(self):
        allowed_paths = [MCWW_WEB_DIR]
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        applyConsoleFilters()
        app, localUrl, shareUrl = self.webUI.launch(
            allowed_paths=allowed_paths,
            favicon_path=logoPath,
            prevent_thread_lock=True,
            auth=opts.MCWW_AUTH,
            pwa=True,
        )
        api: API = API(app)
        while True:
            try:
                time.sleep(1)
                if not self.webUI.is_running:
                    break
            except KeyboardInterrupt:
                break
        self.webUI.close()

