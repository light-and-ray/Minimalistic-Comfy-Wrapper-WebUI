import gradio as gr

class QueueUI:
    def __init__(self):
        self._buildQueueUI()

    def _buildQueueUI(self):
        with gr.Row(elem_classes=["resize-handle-row", "active-workflow-ui"]) as workflowUI:
            with gr.Column(scale=15):
                gr.Markdown("Queue will be here")
            with gr.Column(scale=15):
                gr.Markdown("Inactive queueed workflow will be here")

