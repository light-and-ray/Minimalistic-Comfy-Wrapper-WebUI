import gradio as gr

from mcww import shared

IMAGE_EDITOR_CONTAINER = '''
<div class="mcww-image-editor-container relative w-full aspect-[4/3] rounded-xl overflow-hidden">
        <!-- The two canvases are overlaid here -->
        <canvas id="image-canvas" class="canvas-layer"></canvas>
        <canvas id="drawing-canvas" class="canvas-layer"></canvas>
</div>
'''

COLOR_PICKER = '''
<label for="colorPicker" class="text-gray-600 font-medium">Fill Color:</label>
<input type="color" id="colorPicker" value="#4f46e5" class="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer">
'''

class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()

    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            with gr.Row():
                gr.HTML(COLOR_PICKER)
                clearButton = gr.Button("Clear", scale=0)
                exportButton = gr.Button("Export", scale=0)
            gr.HTML(IMAGE_EDITOR_CONTAINER)
            clearButton.click(
                **shared.runJSFunctionKwargs("clearImageEditor")
            )
            exportButton.click(
                **shared.runJSFunctionKwargs("exportDrawing")
            )

