import gradio as gr

EDITOR_HOTKEYS = '''
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **+/-**       | Zoom In/Out                                               |
| **Space**    | Hold it to pan                                         |
| **Ctrl+Z**   | Undo                                                |
| **Ctrl+Y** / **Ctrl+Shift+Z**  | Redo                                           |
| **[{ / ]}** | Decrease/increase brush size                                      |
'''

def buildImageEditorUI():
    inputImage = gr.Image(elem_classes=["mcww-hidden", "editor-input-image"])
    editor = gr.ImageEditor(type="pil", label="Editor", height="80vh",
        show_download_button=False, elem_classes=["helpers-editor"])
    with gr.Row():
        result = gr.Image(interactive=False, label="Result", height="220px", format="png")
        gr.Markdown(EDITOR_HOTKEYS, elem_classes=["mcww-table", "no-head"])
    inputImage.change(
        fn=lambda x: x,
        inputs=[inputImage],
        outputs=[editor],
    )
    editor.change(
        fn=lambda x: x['composite'],
        inputs=[editor],
        outputs=[result],
    )

