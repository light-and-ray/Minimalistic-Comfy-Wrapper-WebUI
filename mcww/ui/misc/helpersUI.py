import gradio as gr
from mcww import shared
from mcww.ui.compareUI import buildHelperCompareTab
from mcww.ui.misc.loras import buildLorasUI
from mcww.ui.misc.management import buildManagementUI
from mcww.ui.misc.metadata import buildMetadataUI
from mcww.ui.misc.debug import buildDebugUI
from mcww.ui.misc.infoTab import buildInfoTab
from mcww.ui.misc.hotkeys import buildHotkeysUI


def build360VideoUI():
    with gr.Column():
        with gr.Row(height="100vh", elem_classes=["vertically-centred", "grid-on-mobile"]):
            gr.Video(label="360 video", interactive=True, elem_id="video360", scale=4,
                elem_classes=["mcww-other-gallery", "no-compare", "no-pause"])
            gr.HTML(container=False, padding=False, value='<canvas id="video360Slider" class="no-touch-context-menu"></canvas>')
        with gr.Row():
            gr.Markdown("Use to view any kind of looped video with 360 movement - panorama, orbit, rotation, etc", elem_classes=["info-text"])
            with gr.Row(elem_classes=["right-aligned"], scale=0):
                gr.Checkbox(label="Invert", elem_classes=["mcww-swap", "mcww-tiny-element"], value=False, elem_id="video360Inverted")

class HelpersUI:
    def __init__(self):
        self._buildHelpersUI()

    def _buildHelpersUI(self):
        with gr.Column() as self.ui:
            with gr.Tabs(elem_classes=["mcww-page-tabs"]):
                with gr.Tab("Loras"):
                    buildLorasUI()
                with gr.Tab("Management"):
                    buildManagementUI()
                with gr.Tab("Metadata"):
                    buildMetadataUI()
                with gr.Tab("Compare images"):
                    buildHelperCompareTab()
                with gr.Tab("360 Video"):
                    build360VideoUI()
                with gr.Tab("Info"):
                    buildInfoTab()
                with gr.Tab("Hotkeys"):
                    buildHotkeysUI()
                with gr.Tab("Debug"):
                    buildDebugUI()
