import gradio as gr
from mcww.utils import isAudioExtension, saveLogError, isVideoExtension, isImageExtension
from mcww.ui.uiUtils import extractMetadata
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.workflow import Workflow


def buildMetadataUI():
    fileComponent = gr.File(type="filepath", elem_classes=["mcww-metadata-file"])

    @gr.render(inputs=[fileComponent])
    def renderMetadataWorkflow(filePath: str|None):
        if not filePath:
            return
        if isImageExtension(filePath) or isVideoExtension(filePath):
            elem_classes=["mcww-metadata-uploaded"]
            if isVideoExtension(filePath):
                elem_classes += ["no-compare", "no-copy"]
            gr.Gallery(label="Uploaded", value=[filePath], interactive=False, height=250,
                elem_classes=elem_classes, type="filepath", show_download_button=False)
        if isAudioExtension(filePath):
            gr.Audio(label="Uploaded", value=filePath, elem_classes=["mcww-other-gallery", "mcww-metadata-uploaded"])

        metadataPrompt, metadataWorkflow = extractMetadata(filePath)

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

