import gradio as gr
from mcww import shared


def _refreshWarningsDropdown():
    paths = ["-"] + list(shared.workflowsLoadingContext.getDict().keys())
    return gr.Dropdown(choices=paths, value="-")


def _getWarningTable(selected):
    if selected == "-":
        return None
    table = f"**{selected}**\n\n"
    table += "|    |\n"
    table += "|----|\n"
    warnings = shared.workflowsLoadingContext.getDict().get(selected, None)
    if not warnings:
        table += "| nothing |\n"
    else:
        for warning in warnings:
            table += f"| {warning} |\n"
    return table


def buildDebugUI():
    with gr.Row():
        gr.Markdown("You can see here warnings generated during workflows loading. "
                "There can be a reason why some workflows are missing or not work properly")
    with gr.Row(equal_height=True):
        warningsDropdown = gr.Dropdown(label="Workflows Warnings", choices=["-"], value="-", scale=1)
        refresh = gr.Button("Refresh", elem_classes=["mcww-refresh", "mcww-text-button"])
    with gr.Column(elem_classes=["horizontally-centred"]):
        warningTable = gr.Markdown(label="Reason", elem_classes=["mcww-table", "no-head"])
    warningsDropdown.change(
        fn=_getWarningTable,
        inputs=[warningsDropdown],
        outputs=[warningTable],
    )
    gr.on(
        triggers=[refresh.click, shared.webUI.load],
        fn=_refreshWarningsDropdown,
        outputs=[warningsDropdown],
    )

