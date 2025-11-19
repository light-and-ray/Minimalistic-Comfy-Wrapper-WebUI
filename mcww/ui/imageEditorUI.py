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
<input type="color" id="colorPicker" value="{color}" class="w-10 h-10 rounded-full border-2 border-gray-300 cursor-pointer">
'''


class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()

    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            with gr.Row(elem_classes=["vertically-centred"]):
                saveButton = gr.Button("💾 🡠", elem_classes=["small-button"], scale=0)
                saveButton.click(
                    **shared.runJSFunctionKwargs("afterImageEdited")
                )
                backButton = gr.Button("🗑 🡠", elem_classes=["small-button"], scale=0)
                backButton.click(
                    **shared.runJSFunctionKwargs("goBack")
                )
                brushSizeSlider = gr.Slider(interactive=True, label="Brush size", scale=1,
                            elem_id="brushSizeInput", minimum=1, maximum=200, step=1, value=10)
                gr.HTML(COLOR_PICKER.format(color="#cc1b1b"), elem_classes=["color-picker-html"])

            with gr.Row(elem_classes=["block-row-column", "vertically-centred"]):
                with gr.Row(elem_classes=["image-editor-tools-row"]):
                    lassoButton = gr.Button("Lasso 〰️", scale=0, elem_classes=["lasso"], variant='primary')
                    brushButton = gr.Button("Brush 🖌️", scale=0, elem_classes=["brush"])
                    arrowButton = gr.Button("Arrow ➡️", scale=0, elem_classes=["arrow"])
                    eraserButton = gr.Button("Eraser 🧼", scale=0, elem_classes=["eraser"])
                with gr.Row(elem_classes=["block-row-column", "right-aligned"]):
                    redoButton = gr.Button("⟳", scale=0, elem_classes=['mcww-tool', 'force-text-style'])
                    undoButton = gr.Button("⟲", scale=0, elem_classes=['mcww-tool', 'force-text-style'])
                    clearButton = gr.Button("🗑", scale=0, elem_classes=['mcww-tool', 'force-text-style'])

            gr.HTML(IMAGE_EDITOR_CONTAINER)

            gr.Markdown("You can use this editor to draw visual prompt for an image editing model",
                        elem_classes=["mcww-visible", "info-text", "horizontally-centred"])

            # --- Event Listeners for Tools ---
            lassoButton.click(
                **shared.runJSFunctionKwargs("selectLassoTool")
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (True, False, False, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            brushButton.click(
                **shared.runJSFunctionKwargs("selectBrushTool")
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, True, False, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            arrowButton.click(
                **shared.runJSFunctionKwargs("selectArrowTool")
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, False, True, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            eraserButton.click(
                **shared.runJSFunctionKwargs("selectEraserTool")
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, False, False, True)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
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

