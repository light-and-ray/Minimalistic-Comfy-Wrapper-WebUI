import gradio as gr
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


    def _buildCompareUI(self):
        with gr.Column(visible=False) as self.ui:
            imageA_url = gr.Textbox(elem_id="compareImageA_url", elem_classes=["mcww-hidden", "mcww-hidden-parent"])
            imageB_url = gr.Textbox(elem_id="compareImageB_url", elem_classes=["mcww-hidden", "mcww-hidden-parent"])
            with gr.Row(elem_id="compareImageHeadGroup"):
                backButton = gr.Button("🡠", elem_classes=["mcww-tool"])
                swapButton = gr.Button("⇄", elem_classes=["mcww-tool"])
            with gr.Row():
                slider = gr.ImageSlider(show_label=False, height="90vh", elem_classes=["no-compare"],
                    interactive=False, show_download_button=False)
            with gr.Row():
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
