import gradio as gr
from mcww.utils import saveLogError
from mcww.ui.uiUtils import extractMetadata
from mcww.ui.workflowUI import WorkflowUI
from mcww.comfy.workflow import Workflow


def buildMetadataUI():
    file = gr.File()
    metadataPrompt = gr.Json(label="Metadata prompt (API)", render=False)
    metadataWorkflow = gr.Json(label="Metadata workflow (Graph)", render=False)

    @gr.render(inputs=[metadataPrompt, metadataWorkflow])
    def renderMetadataWorkflow(metadataPrompt: dict|None, metadataWorkflow: dict|None):
        for metadata in (metadataPrompt, metadataWorkflow):
            try:
                if not metadata:
                    continue
                workflow = Workflow(metadata)
                if not workflow.isValid():
                    continue
                with gr.Group():
                    WorkflowUI(workflow=workflow, name="", mode=WorkflowUI.Mode.METADATA)
                return
            except Exception as e:
                saveLogError(e, "Error on rendering metadata workflow")
                gr.Markdown(f"{e.__class__.__name__}: {e}", elem_classes=["mcww-visible"])

    metadataPrompt.render()
    metadataWorkflow.render()

    file.change(
        fn=extractMetadata,
        inputs=[file],
        outputs=[metadataPrompt, metadataWorkflow],
    )
