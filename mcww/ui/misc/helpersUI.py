import gradio as gr
from mcww.ui.compareUI import buildHelperCompareTab
from mcww.ui.misc.loras import buildLorasUI
from mcww.ui.misc.management import buildManagementUI
from mcww.ui.misc.metadata import buildMetadataUI
from mcww.ui.misc.debug import buildDebugUI


EDITOR_HOTKEYS = '''
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **+/-**       | Zoom In/Out                                               |
| **Space**    | Hold it to pan                                         |
| **Ctrl+Z**   | Undo                                                |
| **Ctrl+Y** / **Ctrl+Shift+Z**  | Redo                                           |
| **[{ / ]}** | Decrease/increase brush size                                      |
'''

class HelpersUI:
    def __init__(self):
        self._buildHelpersUI()

    def _buildHelpersUI(self):
        with gr.Tabs(visible=False, elem_classes=["tabs-with-hotkeys"]) as self.ui:
            with gr.Tab("Loras"):
                buildLorasUI()
            with gr.Tab("Management"):
                buildManagementUI()
            with gr.Tab("Metadata"):
                buildMetadataUI()
            with gr.Tab("Compare images"):
                buildHelperCompareTab()
            with gr.Tab("Image editor"):
                editor = gr.ImageEditor(type="pil", label="Editor", height="80vh",
                    show_download_button=False, elem_classes=["helpers-editor"])
                with gr.Row():
                    result = gr.Image(interactive=False, label="Result", height="220px")
                    gr.Markdown(EDITOR_HOTKEYS, elem_classes=["mcww-table", "no-head"])
                editor.change(
                    fn=lambda x: x['composite'],
                    inputs=[editor],
                    outputs=[result],
                )
            with gr.Tab("Debug"):
                buildDebugUI()
