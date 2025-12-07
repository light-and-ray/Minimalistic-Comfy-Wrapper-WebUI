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
<input type="color" id="colorPicker" value="{color}" class="{class_}">
'''


class ImageEditorUI:
    def __init__(self):
        self._buildImageEditorUI()


    @staticmethod
    def _selectDrawingToolJs(tool: str):
        return "(() => {globalImageEditor.selectDrawingTool('" + tool + "')})"


    def _buildImageEditorUI(self):
        with gr.Column(visible=False) as self.ui:
            with gr.Row(elem_classes=["vertically-centred"]):
                saveButton = gr.Button("💾 🡠", elem_classes=["small-button", "mcww-save-button"], scale=0)
                saveButton.click(
                    **shared.runJSFunctionKwargs("afterImageEdited")
                )
                backButton = gr.Button("⊘ 🡠", elem_classes=["small-button"], scale=0)
                backButton.click(
                    **shared.runJSFunctionKwargs("goBack")
                )
                gr.Slider(interactive=True, label="Brush size", scale=1,
                            elem_id="brushSizeInput", minimum=1, maximum=200, step=1, value=10)
                gr.HTML(COLOR_PICKER.format(color="#cc1b1b", class_="restore"), elem_classes=["color-picker-html"])

            with gr.Row(elem_classes=["block-row-column", "vertically-centred"]):
                with gr.Row(elem_classes=["image-editor-tools-row", "vertically-centred"]):
                    lassoButton = gr.Button("Lasso 〰️", scale=0, elem_classes=["lasso"], variant='primary')
                    brushButton = gr.Button("Brush 🖌️", scale=0, elem_classes=["brush"])
                    arrowButton = gr.Button("Arrow ➡️", scale=0, elem_classes=["arrow"])
                    eraserButton = gr.Button("Eraser 🧼", scale=0, elem_classes=["eraser"])
                    cropButton = gr.Button("✂️", scale=0, elem_classes=["mcww-tool", "crop"])
                    rotateButton = gr.Button("⤵", scale=0, elem_classes=["mcww-tool", "rotate", 'force-text-style'])
                    gr.on(
                        triggers=[cropButton.click, rotateButton.click],
                        fn=lambda: gr.Info("Not yet implemented", 2)
                    )
                with gr.Row(elem_classes=["block-row-column", "right-aligned", "vertically-centred"]):
                    redoButton = gr.Button("⟳", scale=0, elem_classes=['mcww-tool', 'force-text-style', "mcww-redo"])
                    undoButton = gr.Button("⟲", scale=0, elem_classes=['mcww-tool', 'force-text-style', "mcww-undo"])
                    clearButton = gr.Button("🗑", scale=0, elem_classes=['mcww-tool', 'force-text-style'])

            gr.HTML(IMAGE_EDITOR_CONTAINER)

            gr.Slider(label="Opacity", minimum=0.0, maximum=1.0, value=1.0, elem_classes=["opacity-slider"], interactive=True)

            gr.Markdown("You can use this editor to draw a visual prompt for an image editing model",
                        elem_classes=["mcww-visible", "info-text", "horizontally-centred"])

            lassoButton.click(
                **shared.runJSFunctionKwargs(self._selectDrawingToolJs("lasso"))
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (True, False, False, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            brushButton.click(
                **shared.runJSFunctionKwargs(self._selectDrawingToolJs("brush"))
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, True, False, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            arrowButton.click(
                **shared.runJSFunctionKwargs(self._selectDrawingToolJs("arrow"))
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, False, True, False)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )
            eraserButton.click(
                **shared.runJSFunctionKwargs(self._selectDrawingToolJs("eraser"))
            ).then(
                lambda: [gr.Button(variant='primary') if x else gr.Button(variant='secondary') for x in (False, False, False, True)],
                outputs=[lassoButton, brushButton, arrowButton, eraserButton],
                show_progress='hidden',
            )

            undoButton.click(
                **shared.runJSFunctionKwargs("globalImageEditor.undo")
            )
            redoButton.click(
                **shared.runJSFunctionKwargs("globalImageEditor.redo")
            )
            clearButton.click(
                **shared.runJSFunctionKwargs("globalImageEditor.clearCanvas")
            )

