import gradio as gr
from mcww import shared
from mcww.utils import AttrDict

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
        self.drawingTools = AttrDict()
        self._buildImageEditorUI()


    def getOnToolSelect(self, index):
        def onToolSelect():
            updateList = [gr.Button(variant='secondary')] * len(self.drawingTools)
            updateList[index] = gr.Button(variant='primary')
            return updateList
        return onToolSelect


    def _buildImageEditorUI(self):
        with gr.Column() as self.ui:
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
                            elem_id="brushSizeInput", minimum=1, maximum=200, step=0.5, value=10)
                gr.HTML(COLOR_PICKER.format(color="#cc1b1b", class_="restore"), elem_classes=["color-picker-html"])

            with gr.Row(elem_classes=["block-row-column", "vertically-centred"]):
                with gr.Row(elem_classes=["image-editor-tools-row", "vertically-centred"]):
                    self.drawingTools.lasso = gr.Button("Lasso 〰️", scale=0, variant='primary')
                    self.drawingTools.brush = gr.Button("Brush 🖌️", scale=0)
                    self.drawingTools.arrow = gr.Button("Arrow ➡️", scale=0)
                    self.drawingTools.eraser = gr.Button("Eraser 🧼", scale=0)
                    self.drawingTools.crop = gr.Button("✂️", scale=0, elem_classes=["mcww-tool"])
                    rotateButton = gr.Button("⤵", scale=0, elem_classes=["mcww-tool", "rotate", 'force-text-style'])
                with gr.Row(elem_classes=["block-row-column", "right-aligned", "vertically-centred"]):
                    redoButton = gr.Button("⟳", scale=0, elem_classes=['mcww-tool', 'force-text-style', "mcww-redo"])
                    undoButton = gr.Button("⟲", scale=0, elem_classes=['mcww-tool', 'force-text-style', "mcww-undo"])
                    clearButton = gr.Button("🗑", scale=0, elem_classes=['mcww-tool', 'force-text-style'])

            gr.HTML(IMAGE_EDITOR_CONTAINER)

            gr.Slider(label="Opacity", minimum=0.0, maximum=1.0, value=1.0, elem_classes=["opacity-slider"], interactive=True)

            gr.Markdown("You can use this editor to draw a visual prompt for an image editing model",
                        elem_classes=["mcww-visible", "info-text", "horizontally-centred"])

            index = 0
            for name, component in self.drawingTools.items():
                component.elem_classes += [name]

                component.click(
                    **shared.runJSFunctionKwargs( "(() => {globalImageEditor.selectDrawingTool('"+name+"')})")
                ).then(
                    fn=self.getOnToolSelect(index),
                    outputs=list(self.drawingTools.values()),
                    show_progress='hidden',
                )
                index += 1

            rotateButton.click(
                **shared.runJSFunctionKwargs("globalImageEditor.rotate")
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

