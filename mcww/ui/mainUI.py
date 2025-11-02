from mcww.ui.mcwwAPI import API
import gradio as gr
import os, time, uuid
from mcww import opts
from mcww.utils import applyConsoleFilters, saveLogError
from mcww.ui.uiUtils import (ifaceCSS, getIfaceCustomHead, logoPath, MCWW_WEB_DIR,
    showRenderingErrorGradio, getStorageKey, getStorageEncryptionKey, getMcwwLoaderHTML
)
from mcww.ui.webUIState import WebUIState
from mcww.ui.queueUI import QueueUI
from mcww.ui.projectUI import ProjectUI
from mcww.ui.sidebarUI import SidebarUI
from mcww.ui.helpersUI import HelpersUI

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
            refreshProjectTrigger = gr.Textbox(visible=False)
            refreshProjectKwargs: dict = dict(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshProjectTrigger]
            )
            webUIStateComponent = gr.BrowserState(
                default_value=WebUIState.DEFAULT_WEBUI_STATE_JSON,
                storage_key=getStorageKey(), secret=getStorageEncryptionKey())

            with gr.Sidebar(width=100, open=True):
                sidebarUI = SidebarUI(self.webUI, webUIStateComponent,
                        refreshProjectTrigger, refreshProjectKwargs)


            QueueUI(sidebarUI.mainUIPageRadio, self.webUI)

            ProjectUI(sidebarUI.mainUIPageRadio, self.webUI, webUIStateComponent,
                        refreshProjectTrigger, refreshProjectKwargs)

            gr.HTML(getMcwwLoaderHTML(["startup-loading"]))

            HelpersUI(sidebarUI.mainUIPageRadio, self.webUI)

            @gr.render(
                triggers=[sidebarUI.mainUIPageRadio.change],
                inputs=[sidebarUI.mainUIPageRadio],
            )
            def _(mainUIPage: str):
                try:
                    if mainUIPage == "settings":
                        gr.Markdown("Settings will be here")
                    elif mainUIPage == "wolf3d":
                        from mcww.ui.uiUtils import easterEggWolf3dIframe
                        gr.HTML(easterEggWolf3dIframe)
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

