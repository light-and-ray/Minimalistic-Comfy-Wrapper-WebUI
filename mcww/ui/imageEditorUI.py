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
<label for="colorPicker" class="color-picker-label">Color:</label>
<input type="color" id="colorPicker" value="#4f46e5" class="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer">
<label for="brushSizeInput" class="color-picker-label ml-4">Size:</label>
<input type="number" id="brushSizeInput" value="5" min="1" max="50" class="w-16 h-10 text-center rounded-lg border-2 border-gray-300">
'''


class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()

    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            # --- Tool Selection Row (NEW) ---
            with gr.Row(scale=1):
                lassoButton = gr.Button("Lasso 〰️", scale=1)
                brushButton = gr.Button("Brush 🖌️", scale=1)
                arrowButton = gr.Button("Arrow ➡️", scale=1)

            with gr.Row(scale=1):
                gr.HTML(COLOR_PICKER)
                undoButton = gr.Button("Undo", scale=0)
                redoButton = gr.Button("Redo", scale=0)
                clearButton = gr.Button("Clear", scale=0)
                exportButton = gr.Button("Export", scale=0)

            gr.HTML(IMAGE_EDITOR_CONTAINER)

            # --- Event Listeners for Tools ---
            lassoButton.click(
                **shared.runJSFunctionKwargs("selectLassoTool")
            )
            brushButton.click(
                **shared.runJSFunctionKwargs("selectBrushTool")
            )
            arrowButton.click(
                **shared.runJSFunctionKwargs("selectArrowTool")
            )

            # --- Existing Listeners ---
            undoButton.click(
                **shared.runJSFunctionKwargs("undoDrawing")
            )
            redoButton.click(
                **shared.runJSFunctionKwargs("redoDrawing")
            )
            clearButton.click(
                **shared.runJSFunctionKwargs("clearImageEditor")
            )
            exportButton.click(
                **shared.runJSFunctionKwargs("exportDrawing")
            )
            