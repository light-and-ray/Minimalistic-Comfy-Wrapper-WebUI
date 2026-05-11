import gradio as gr
from mcww import shared, opts
from mcww.utils import isImageExtension, isAudioExtension, isVideoExtension, isModel3DExtension, read_string_from_file, markdownHandleThinkTag
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
                    gr.Markdown("You can use this as a model viewer. But 3D models in workflows are not supported yet",
                                                                elem_classes=["info-text", "mcww-visible"])
                if filePath.lower().endswith(".md"):
                    with gr.Group(elem_classes=["mcww-pseudo-gallery", "opened-markdown-file-view"]):
                        elem_classes = ["mcww-visible", "allow-pwa-select", "markdown-view"]
                        if opts.options.protectUrlsInMarkdownOutput:
                            elem_classes.append("mcww-protect-links")
                        text = read_string_from_file(filePath)
                        text = markdownHandleThinkTag(text)
                        gr.Markdown(value=text, elem_classes=elem_classes)
            except Exception as e:
                showRenderingErrorGradio(e, "Error on rendering file open page")

        with gr.Row(equal_height=True, elem_classes=["horizontally-centred", "file-open-buttons-new-window"]):
            goToProjectPageButton = gr.Button("Go to project page", scale=0, elem_classes=["label-button"])
            goToProjectPageButton.click(
                **shared.runJSFunctionKwargs('ensureProjectIsSelected')
            )
            gr.Markdown("**Or close this window**", elem_classes=["mcww-visible", "info-text"])
        with gr.Row(equal_height=True, elem_classes=["file-open-buttons-same-window", "mcww-hidden"]):
            goBackButton = gr.Button("🡠 Go back", scale=0, elem_classes=["label-button", "click-on-escape"])
            goBackButton.click(
                **shared.runJSFunctionKwargs('goBack')
            )
        openedFile.change(
            **shared.runJSFunctionKwargs("afterFileOpened")
        )
    return fileOpenUI

