from mcww.ui.mcwwAPI import API
import gradio as gr
import os, time, uuid
from mcww import opts, queueing
from mcww.utils import applyConsoleFilters, RESTART_TMP_FILE
from mcww.ui.uiUtils import (ifaceCSS, getIfaceCustomHead, logoPath, MCWW_WEB_DIR, MAIN_UI_PAGES,
    getStorageKey, getStorageEncryptionKey, getMcwwLoaderHTML
)
from mcww.ui.webUIState import WebUIState
from mcww.ui.queueUI import QueueUI
from mcww.ui.projectUI import ProjectUI
from mcww.ui.sidebarUI import SidebarUI
from mcww.ui.helpersUI import HelpersUI
from mcww.ui.compareUI import CompareUI

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

            queueUI = QueueUI(self.webUI)
            projectUI = ProjectUI(self.webUI, webUIStateComponent,
                        refreshProjectTrigger, refreshProjectKwargs)
            gr.HTML(getMcwwLoaderHTML(["startup-loading"]))
            helpersUI = HelpersUI(sidebarUI.mainUIPageRadio, self.webUI)
            with gr.Column(visible=False) as settingsUI:
                gr.Markdown("Settings will be here", elem_classes=["mcww-visible"])
            compareUI = CompareUI()
            with gr.Column(visible=False) as wold3dUI:
                from mcww.ui.uiUtils import easterEggWolf3dIframe
                gr.HTML(easterEggWolf3dIframe)

            @gr.on(
                triggers=[sidebarUI.mainUIPageRadio.change],
                inputs=[sidebarUI.mainUIPageRadio],
                outputs=[queueUI.ui, projectUI.ui, helpersUI.ui, settingsUI, compareUI.ui, wold3dUI],
                show_progress='hidden',
            )
            def onMainUIPageChange(mainUIPage: str):
                result = [False] * len(MAIN_UI_PAGES)
                selectedIndex = MAIN_UI_PAGES.index(mainUIPage)
                result[selectedIndex] = True
                return [gr.update(visible=x) for x in result]



    def launch(self):
        if os.path.exists(RESTART_TMP_FILE):
            print(f"*** '{RESTART_TMP_FILE}' file found, this means that launch script doesn't handle it correctly")
            os.remove(RESTART_TMP_FILE)
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
                queueing.queue.iterateQueueProcessingLoop()
                time.sleep(0.05)
                if not self.webUI.is_running:
                    break
            except KeyboardInterrupt:
                break
        self.webUI.close()

