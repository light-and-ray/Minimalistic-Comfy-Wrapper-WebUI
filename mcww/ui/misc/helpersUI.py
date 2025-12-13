import gradio as gr
from mcww.ui.compareUI import buildHelperCompareTab
from mcww.ui.misc.loras import buildLorasUI
from mcww.ui.misc.management import buildManagementUI
from mcww.ui.misc.metadata import buildMetadataUI
from mcww.ui.misc.debug import buildDebugUI
from mcww.ui.misc.infoTab import buildInfoTab
from mcww.ui.misc.hotkeys import buildHotkeysUI


class HelpersUI:
    def __init__(self):
        self._buildHelpersUI()

    def _buildHelpersUI(self):
        with gr.Tabs(visible=False, elem_classes=["tabs-with-hotkeys", "show-tab-in-title"]) as self.ui:
            with gr.Tab("Loras"):
                buildLorasUI()
            with gr.Tab("Management"):
                buildManagementUI()
            with gr.Tab("Metadata"):
                buildMetadataUI()
            with gr.Tab("Compare images"):
                buildHelperCompareTab()
            with gr.Tab("Info"):
                buildInfoTab()
            with gr.Tab("Hotkeys"):
                buildHotkeysUI()
            with gr.Tab("Debug"):
                buildDebugUI()
