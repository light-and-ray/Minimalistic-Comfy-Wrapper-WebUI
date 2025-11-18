import gradio as gr

from mcww import shared

IMAGE_EDITOR_CONTAINER = '''
<div class="mcww-canvas-wrapper">
    <div class="mcww-image-editor-container relative rounded-xl overflow-hidden">
        <div id="image-editor-bg" class="canvas-layer" style="z-index: 1;"></div>
        <canvas id="image-canvas" class="canvas-layer" style="z-index: 2;"></canvas>
        <canvas id="drawing-canvas" class="canvas-layer" style="z-index: 3;"></canvas>
    </div>
</div>
'''

COLOR_PICKER = '''
<label for="colorPicker" class="text-gray-600 font-medium">Fill Color:</label>
<input type="color" id="colorPicker" value="#4f46e5" class="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer">
'''

# ... (Previous code remains the same) ...

class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()

    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            with gr.Row():
                gr.HTML(COLOR_PICKER)
                undoButton = gr.Button("Undo", scale=0) # NEW BUTTON
                redoButton = gr.Button("Redo", scale=0) # NEW BUTTON
                clearButton = gr.Button("Clear", scale=0)
                exportButton = gr.Button("Export", scale=0)
            gr.HTML(IMAGE_EDITOR_CONTAINER)

            # NEW FUNCTION CALLS
            undoButton.click(
                **shared.runJSFunctionKwargs("undoDrawing")
            )
            redoButton.click(
                **shared.runJSFunctionKwargs("redoDrawing")
            )
            # Existing function calls
            clearButton.click(
                **shared.runJSFunctionKwargs("clearImageEditor")
            )
            exportButton.click(
                **shared.runJSFunctionKwargs("exportDrawing")
            )
            