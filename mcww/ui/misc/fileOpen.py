import gradio as gr
from mcww import shared
from mcww.utils import isImageExtension, isAudioExtension, isVideoExtension, isModel3DExtension
from mcww.ui.uiUtils import showRenderingErrorGradio

def makeFileOpenUI():
    with gr.Column() as fileOpenUI:
        openedFile = gr.File(label="Opened file", elem_classes=["opened-file", "upload-gallery"])
        @gr.render(triggers=[openedFile.change], inputs=[openedFile])
        def renderOpenedFile(filePath: str):
            try:
                if not filePath: return
                if isImageExtension(filePath) or isVideoExtension(filePath):
                    elem_classes=[]
                    if isVideoExtension(filePath):
                        elem_classes += ["no-compare"]
                    gr.Gallery(label="Opened", value=[filePath], interactive=False, height=250,
                            elem_classes=elem_classes, type="filepath", show_download_button=False)
                if isAudioExtension(filePath):
                    gr.Audio(label="Opened", value=filePath, elem_classes=["mcww-other-gallery", "no-compare"])
                if isModel3DExtension(filePath):
                    gr.Model3D(label="Opened", value=filePath, elem_classes=["mcww-other-gallery", "no-compare", "no-open", "no-copy"])
                    gr.Markdown("3D models in workflows are not supported in this MCWW version due to lack "
                                    "of a really good open source 3d model generator, but you can use it as a model viewer",
                                                        elem_classes=["info-text", "mcww-visible"])
            except Exception as e:
                showRenderingErrorGradio(e, "Error on rendering file open page")

        with gr.Row(equal_height=True, elem_classes=["horizontally-centred"]):
            goToProjectPageButton = gr.Button("Go to project page", scale=0, elem_classes=["label-button", "click-on-escape"])
            goToProjectPageButton.click(
                **shared.runJSFunctionKwargs('goBack')
            )
            gr.Markdown("**Or close this window**", elem_classes=["mcww-visible", "info-text"])
    return fileOpenUI

