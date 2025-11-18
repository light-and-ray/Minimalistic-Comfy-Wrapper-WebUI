import gradio as gr
from mcww import shared

IMAGE_EDITOR_CONTAINER = '''
<div class="mcww-canvas-wrapper">
    <div class="mcww-image-editor-container relative rounded-xl overflow-hidden">
        <div id="image-editor-bg" class="canvas-layer" style="z-index: 1;"></div>
        <canvas id="image-canvas" class="canvas-layer"></canvas>
        <canvas id="brush-preview-canvas" class="canvas-layer"></canvas>
        <canvas id="drawing-canvas" class="canvas-layer"></canvas>
    </div>
</div>
'''

COLOR_PICKER = '''
<label for="colorPicker" class="color-picker-label">Color:</label>
<input type="color" id="colorPicker" value="#4f46e5" class="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer">
'''


class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()

    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            with gr.Row(elem_classes=["vertically-centred"]):
                with gr.Column():
                    with gr.Row():
                        lassoButton = gr.Button("Lasso 〰️", scale=0)
                        brushButton = gr.Button("Brush 🖌️", scale=0)
                        arrowButton = gr.Button("Arrow ➡️", scale=0)

                with gr.Column():
                    with gr.Row():
                        gr.HTML(COLOR_PICKER)
                        brushSizeSlider = gr.Slider(interactive=True, label="Brush size", scale=0,
                                    elem_id="brushSizeInput", minimum=1, maximum=200, step=1, value=20)
                        undoButton = gr.Button("⟲", scale=0, elem_classes=['mcww-tool', 'force-text-style'])
                        redoButton = gr.Button("⟳", scale=0, elem_classes=['mcww-tool', 'force-text-style'])
                        clearButton = gr.Button("🗑", scale=0, elem_classes=['mcww-tool', 'force-text-style'])

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
            brushSizeSlider.change(
                fn=lambda x: None,
                inputs=[brushSizeSlider],
                js="setBrushSize",
                preprocess=False,
                postprocess=False,
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

