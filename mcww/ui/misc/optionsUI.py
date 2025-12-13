import gradio as gr
from mcww import opts


class OptionsUI:
    def __init__(self):
        self._buildOptionsUI()


    @staticmethod
    def _onApplyChanges(
        accentColorHue,
        maxQueueSize,
        showToggleDarkLightButton,
        showRunButtonCopy,
    ):
        opts.options.primaryHue = accentColorHue
        opts.options.maxQueueSize = maxQueueSize
        opts.options.showToggleDarkLightButton = showToggleDarkLightButton
        opts.options.showRunButtonCopy = showRunButtonCopy
        opts.saveOptions()
        gr.Info("Options saved, restart UI to apply some of them", 4)


    def _buildOptionsUI(self):
        with gr.Column(visible=False, elem_classes=["options-main-column"]) as self.ui:
            with gr.Row(equal_height=True):
                accentColorHue = gr.Slider(label=f"Accent color hue", show_reset_button=False,
                                    value=opts.options.primaryHue, minimum=0, maximum=360, step=1)
                accentColorHuePreview = gr.ColorPicker(interactive=False, elem_classes=["accent-color-preview"],
                                    value=opts.getThemeColor(opts.options.primaryHue).c500, show_label=False, scale=0)
                accentColorHue.change(
                    fn=lambda hue: opts.getThemeColor(hue).c500,
                    inputs=[accentColorHue],
                    outputs=[accentColorHuePreview],
                    show_progress='hidden',
                )
            maxQueueSize = gr.Slider(value=opts.options.maxQueueSize, minimum=10, maximum=999, step=1,
                                                show_reset_button=False, label="Max queue size")
            showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme',
                            value=opts.options.showToggleDarkLightButton)
            showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI',
                            value=opts.options.showRunButtonCopy)

            applyChanges = gr.Button(value="Apply changes", elem_classes=["mcww-save"])
            applyChanges.click(
                fn=self._onApplyChanges,
                inputs=[
                    accentColorHue,
                    maxQueueSize,
                    showToggleDarkLightButton,
                    showRunButtonCopy,
                ]
            )
