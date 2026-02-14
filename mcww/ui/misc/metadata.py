import gradio as gr
from mcww.utils import saveLogError, isVideoExtension, isImageExtension, isAudioExtension
from mcww.ui.uiUtils import extractMetadata
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.workflow import Workflow


def buildMetadataUI():
    with gr.Tabs():
        with gr.Tab(label="Any file") as anyFileTab:
            autoComponent = gr.File(label="File", type="filepath", elem_classes=["mcww-other-gallery", "mcww-metadata-file"])
        with gr.Tab(label="Image") as imageTab:
            imageComponent = gr.Image(label="Image", type="filepath", height=250, sources=["upload"])
        with gr.Tab(label="Video") as videoTab:
            videoComponent = gr.Video(label="Video", height=250, sources=["upload"], elem_classes=["mcww-other-gallery"])
        with gr.Tab(label="Audio") as audioTab:
            audioComponent = gr.Audio(label="Audio", type="filepath", sources=["upload"], elem_classes=["mcww-other-gallery"])
    selectedTab = gr.Textbox(visible=False, value="anyFileTab")
    anyFileTab.select(
        fn=lambda: "anyFileTab",
        outputs=[selectedTab],
    )
    imageTab.select(
        fn=lambda: "imageTab",
        outputs=[selectedTab],
    )
    videoTab.select(
        fn=lambda: "videoTab",
        outputs=[selectedTab],
    )
    audioTab.select(
        fn=lambda: "audioTab",
        outputs=[selectedTab],
    )

    @gr.render(inputs=[autoComponent, imageComponent, videoComponent, audioComponent, selectedTab])
    def renderMetadataWorkflow(autoPath: str, imagePath: str, videoPath: str, audioPath: str, selectedTab: str):
        filePath = None
        if selectedTab == "anyFileTab":
            filePath = autoPath
        elif selectedTab == "imageTab":
            filePath = imagePath
        elif selectedTab == "videoTab":
            filePath = videoPath
        elif selectedTab == "audioTab":
            filePath = audioPath
        if not filePath:
            return
        if selectedTab == "anyFileTab":
            if isImageExtension(filePath) or isVideoExtension(filePath):
                elem_classes=["mcww-metadata-uploaded"]
                if isVideoExtension(filePath):
                    elem_classes += ["no-compare", "no-copy"]
                gr.Gallery(label="Uploaded", value=[filePath], interactive=False, height=250,
                        elem_classes=elem_classes, type="filepath", show_download_button=False)
            if isAudioExtension(filePath):
                gr.Audio(label="Uploaded", value=filePath, elem_classes=["mcww-other-gallery", "mcww-metadata-uploaded"])
        metadataPrompt, metadataWorkflow, metadataOther = extractMetadata(filePath)

        for metadata in (metadataPrompt, metadataWorkflow):
            try:
                if not metadata:
                    continue
                workflow = Workflow(metadata)
                if not workflow.isValid():
                    continue
                with gr.Group(elem_classes=["metadata-workflow-group"]):
                    WorkflowUI(workflow=workflow, name="", mode=WorkflowUI.Mode.METADATA)
                break
            except Exception as e:
                saveLogError(e, "Error on rendering metadata workflow")
                gr.Markdown(f"{e.__class__.__name__}: {e}", elem_classes=["mcww-visible"])

        if metadataPrompt:
            gr.Json(label="Metadata prompt (API format)", value=metadataPrompt, elem_classes=["allow-pwa-select"],)
        if metadataWorkflow:
            gr.Json(label="Metadata workflow (Graph format)", value=metadataWorkflow, elem_classes=["allow-pwa-select"],)
        if isinstance(metadataOther, str) and metadataOther:
            gr.Textbox(label="Other metadata", value=metadataOther, elem_classes=["allow-pwa-select"])

