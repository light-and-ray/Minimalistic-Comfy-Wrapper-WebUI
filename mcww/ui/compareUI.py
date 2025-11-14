import gradio as gr
from PIL import Image
from mcww import shared
from mcww.comfy.comfyFile import ImageData

class CompareUI:
    def __init__(self):
        self._buildCompareUI()

    @staticmethod
    def onCompareClick(imageA_url, imageB_url):
        if not imageA_url or not imageB_url:
            return None
        imageA = ImageData(url=imageA_url, orig_name="imageA")
        imageB = ImageData(url=imageB_url, orig_name="imageB")
        return (imageA, imageB)


    @staticmethod
    def makeOpacitySlider():
        slider = gr.Slider(label="Opacity", minimum=0.0, maximum=1.0, value=1.0, elem_classes=["opacity-slider"])
        slider.change(
            fn=lambda x: None,
            inputs=[slider],
            js='updateCompareOpacity',
            preprocess=False,
            postprocess=False,
        )
        return slider


    def _buildCompareUI(self):
        with gr.Column(visible=False) as self.ui:
            imageA_url = gr.Textbox(elem_id="compareImageA_url", elem_classes=["mcww-hidden", "mcww-hidden-parent"])
            imageB_url = gr.Textbox(elem_id="compareImageB_url", elem_classes=["mcww-hidden", "mcww-hidden-parent"])
            with gr.Row(elem_id="compareImageHeadGroup"):
                backButton = gr.Button("🡠", elem_classes=["mcww-tool"])
                swapButton = gr.Button("⇄", elem_classes=["mcww-tool", "mcww-swap"])
            with gr.Row():
                slider = gr.ImageSlider(show_label=False, height="90vh", elem_classes=["no-compare", "no-copy"],
                    interactive=False, show_download_button=False)
            with gr.Row():
                self.makeOpacitySlider()
            compareButton = gr.Button(elem_id="compareImagesButton", elem_classes=["mcww-hidden"])

        compareButton.click(
            fn=self.onCompareClick,
            inputs=[imageA_url, imageB_url],
            outputs=[slider],
            postprocess=False,
            show_progress='hidden',
        )

        swapButton.click(
            fn=lambda a, b: (b, a),
            inputs=[imageA_url, imageB_url],
            outputs=[imageA_url, imageB_url],
        ).then(
            fn=self.onCompareClick,
            inputs=[imageA_url, imageB_url],
            outputs=[slider],
            postprocess=False,
        ).then(
            **shared.runJSFunctionKwargs("swapGlobalImagesAB")
        )

        backButton.click(
            **shared.runJSFunctionKwargs("goBack")
        )


def buildHelperCompareTab():
    with gr.Tabs():
        with gr.Tab("From A and B") as tabAB:
            with gr.Row(elem_classes=["grid-on-mobile"]):
                imageA = gr.Image(label="A", type="pil", height="250px", elem_classes=["no-compare", "no-camera"])
                swapButton = gr.Button("⇄", elem_classes=["mcww-tool", "mcww-swap"])
                imageB = gr.Image(label="B", type="pil", height="250px", elem_classes=["no-compare", "no-camera"])
        with gr.Tab("From Stitched") as tabStitched:
            with gr.Row():
                imageStitched = gr.Image(label="Stitched", type="pil", height="250px", elem_classes=["no-compare", "no-camera"])
                with gr.Column(elem_classes=["vertically-centred"]):
                    stitchedMode = gr.Radio(value="horizontally", choices=["horizontally", "vertically"], show_label=False)
                    stitchedReversed = gr.Checkbox(label="Reversed", value=False, elem_classes=["mcww-swap"])
    with gr.Row():
        slider = gr.ImageSlider(show_label=False, height="90vh", elem_classes=["no-compare", "no-copy"],
                interactive=False, show_download_button=False)
    with gr.Row():
        CompareUI.makeOpacitySlider()

    @gr.on(
        triggers=[imageA.change, imageB.change, tabAB.select],
        inputs=[imageA, imageB],
        outputs=[slider],
    )
    def onHelperImageCompareChange(imageA, imageB):
        if not imageA or not imageB:
            return None
        return (imageA, imageB)

    @gr.on(
        triggers=[imageStitched.change, stitchedReversed.change, stitchedMode.change, tabStitched.select],
        inputs=[imageStitched, stitchedReversed, stitchedMode],
        outputs=[slider],
    )
    def onImageStitchedChange(stitched: Image.Image, reversed: bool, mode: str):
        if not stitched:
            return None
        width, height = stitched.size
        if mode == "horizontally":
            half_width = width // 2
            if reversed:
                imageA = stitched.crop((half_width, 0, width, height))
                imageB = stitched.crop((0, 0, half_width, height))
            else:
                imageB = stitched.crop((half_width, 0, width, height))
                imageA = stitched.crop((0, 0, half_width, height))
        elif mode == "vertically":
            half_height = height // 2
            if reversed:
                imageA = stitched.crop((0, half_height, width, height))
                imageB = stitched.crop((0, 0, width, half_height))
            else:
                imageB = stitched.crop((0, half_height, width, height))
                imageA = stitched.crop(box=(0, 0, width, half_height))
        return (imageA, imageB)

    swapButton.click(
        fn=lambda a, b: (b, a),
        inputs=[imageA, imageB],
        outputs=[imageA, imageB],
    )

