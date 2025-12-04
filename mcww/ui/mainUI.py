from mcww.ui.mcwwAPI import API
import gradio as gr
import os, time, uuid
from mcww import opts, queueing, shared
from mcww.comfy.messages import Messages
from mcww.utils import ( applyConsoleFilters, RESTART_TMP_FILE, hotkeysReference,
    getStorageKey, getStorageEncryptionKey, initClientID,
)
from mcww.ui.uiUtils import (ifaceCSS, getIfaceCustomHead, logoPath, MCWW_WEB_DIR, MAIN_UI_PAGES,
    getMcwwLoaderHTML
)
from mcww.ui.webUIState import WebUIState
from mcww.ui.queueUI import QueueUI
from mcww.ui.projectUI import ProjectUI
from mcww.ui.sidebarUI import SidebarUI
from mcww.ui.misc.helpersUI import HelpersUI
from mcww.ui.compareUI import CompareUI
from mcww.ui.presetsUI import PresetsUI
from mcww.ui.imageEditorUI import ImageEditorUI

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "0")


class MinimalisticComfyWrapperWebUI:
    def __init__(self):
        pass


    def _initWebUI(self):
        with gr.Blocks(analytics_enabled=False,
                       title=opts.WEBUI_TITLE,
                       theme=opts.GRADIO_THEME,
                       css=ifaceCSS,
                       head=getIfaceCustomHead()) as self.webUI:
            shared.webUI = self.webUI
            refreshProjectTrigger = gr.Textbox(visible=False)
            refreshProjectKwargs: dict = dict(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshProjectTrigger]
            )
            webUIStateComponent = gr.BrowserState(
                default_value=WebUIState.DEFAULT_WEBUI_STATE_JSON,
                storage_key=getStorageKey(), secret=getStorageEncryptionKey())
            shared.dummyComponent = gr.Textbox(visible=False)
            def _runJSFunctionKwargs(jsFunctions) -> dict:
                if isinstance(jsFunctions, str):
                    jsFunctions = [jsFunctions]
                jsCode = '(async function (...args) {'
                for jsFunction in jsFunctions:
                    jsCode += f"await {jsFunction}();"
                jsCode += '})'
                return dict(
                        fn=lambda x: x,
                        inputs=[shared.dummyComponent],
                        outputs=[shared.dummyComponent],
                        js=jsCode,
                )
            shared.runJSFunctionKwargs = _runJSFunctionKwargs

            with gr.Sidebar(width=100, open=True):
                sidebarUI = SidebarUI(webUIStateComponent, refreshProjectTrigger, refreshProjectKwargs)

            queueUI = QueueUI()
            projectUI = ProjectUI(webUIStateComponent, refreshProjectTrigger, refreshProjectKwargs)
            gr.HTML(getMcwwLoaderHTML(["startup-loading"]))
            helpersUI = HelpersUI()
            with gr.Column(visible=False) as optionsUI:
                gr.Markdown("Options will be here", elem_classes=["mcww-visible"])
                gr.Markdown(hotkeysReference, elem_classes=["mcww-table", "no-head"])
            compareUI = CompareUI()
            shared.presetsUIStateComponent = gr.State()
            presetsUI = PresetsUI()
            imageEditorUI = ImageEditorUI()
            with gr.Column(visible=False) as wold3dUI:
                from mcww.ui.uiUtils import easterEggWolf3dIframe
                gr.HTML(easterEggWolf3dIframe)

            @gr.on(
                triggers=[sidebarUI.mainUIPageRadio.change],
                inputs=[sidebarUI.mainUIPageRadio],
                outputs=[queueUI.ui, projectUI.ui, helpersUI.ui, optionsUI, compareUI.ui, presetsUI.ui, imageEditorUI.ui, wold3dUI],
                show_progress='hidden',
            )
            def onMainUIPageChange(mainUIPage: str):
                result = [False] * len(MAIN_UI_PAGES)
                selectedIndex = MAIN_UI_PAGES.index(mainUIPage)
                result[selectedIndex] = True
                return [gr.update(visible=x) for x in result]



    def launch(self):
        queueing.initQueue()
        if os.path.exists(RESTART_TMP_FILE):
            print(f"*** '{RESTART_TMP_FILE}' file found, this means that launch script doesn't handle it correctly")
            os.remove(RESTART_TMP_FILE)
        allowed_paths = [MCWW_WEB_DIR, os.path.join(opts.STORAGE_DIRECTORY, "thumbnails")]
        if opts.FILE_CONFIG.mode != opts.FilesMode.DIRECT_LINKS:
            allowed_paths.append(opts.FILE_CONFIG.input_dir)
            allowed_paths.append(opts.FILE_CONFIG.output_dir)
        self._initWebUI()
        applyConsoleFilters()

        app, shared.localUrl, shareUrl = shared.webUI.launch(
            allowed_paths=allowed_paths,
            favicon_path=logoPath,
            prevent_thread_lock=True,
            auth=opts.MCWW_AUTH,
            pwa=True,
            share_server_address=os.environ.get("FRP_SHARE_SERVER_ADDRESS", None),
            share_server_protocol=os.environ.get("FRP_SHARE_SERVER_PROTOCOL", None),
            share_server_tls_certificate=os.environ.get("FRP_SHARE_SERVER_TLS_CERTIFICATE", None),
        )
        initClientID()
        shared.api: API = API(app)
        shared.messages: Messages = Messages()
        last_queue_save_time = time.time()

        while True:
            try:
                queueing.queue.iterateQueueProcessingLoop()
                if time.time() - last_queue_save_time >= queueing.AUTOSAVE_INTERVAL:
                    queueing.saveQueue()
                    last_queue_save_time = time.time()
                time.sleep(0.05)
                if not shared.webUI.is_running:
                    break
            except KeyboardInterrupt:
                break
        shared.webUI.close()
        queueing.saveQueue()
        shared.messages.close()

