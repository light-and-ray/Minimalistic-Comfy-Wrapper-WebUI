import gradio as gr
from mcww import shared


def _refreshWorkflows():
    paths = ["-"] + list(shared.rejectedWorkflows.keys())
    return gr.Dropdown(choices=paths, value="-")


def buildDebugUI():
    with gr.Row():
        gr.Markdown("You can see here a reason why some workflows are not shown in the main UI.\\\n"
            "If you don't see your workflow even here, it probably doesn't have nodes with mandatory categories: "
            '"prompt" or "output".')
    with gr.Row(equal_height=True):
        workflowPaths = gr.Dropdown(label="Rejected workflows", choices=["-"], value="-", scale=1)
        reason = gr.Textbox(label="Reason", lines=2, scale=4)
        refresh = gr.Button("Refresh", elem_classes=["mcww-refresh", "mcww-text-button"])
        workflowPaths.change(
            lambda x: shared.rejectedWorkflows.get(x, ""),
            inputs=[workflowPaths],
            outputs=[reason],
        )
        gr.on(
            triggers=[refresh.click, shared.webUI.load],
            fn=_refreshWorkflows,
            outputs=[workflowPaths],
        )