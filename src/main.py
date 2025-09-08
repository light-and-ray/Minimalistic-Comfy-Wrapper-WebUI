import gradio as gr

with gr.Blocks(analytics_enabled=False) as webui:
    with gr.Row():
        with gr.Column():
            gr.Markdown("Column 1")
        with gr.Column():
            gr.Markdown("Column 2")

webui.launch()
