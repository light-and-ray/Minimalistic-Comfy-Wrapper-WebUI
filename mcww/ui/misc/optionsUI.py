import gradio as gr
from mcww import opts
from mcww.utils import AttrDict
from mcww.ui.uiUtils import ButtonWithConfirm


class OptionsUI:
    def __init__(self):
        self._components = AttrDict()
        self._buildOptionsUI()


    def _onApplyChanges(self, *args):
        for key, value in zip(self._components.keys(), args):
            setattr(opts.options, key, value)
        opts.saveOptions()
        gr.Info("Options saved, restart UI to apply some of them", 4)


    def _buildOptionsUI(self):
        with gr.Column(visible=False, elem_classes=["options-main-column"]) as self.ui:
            with gr.Group():
                with gr.Row(equal_height=True):
                    self._components.primaryHue = gr.Slider(label=f"Accent color hue", show_reset_button=False,
                                        value=opts.options.primaryHue, minimum=0, maximum=360, step=1)
                    primaryHuePreview = gr.ColorPicker(interactive=False, elem_classes=["accent-color-preview"],
                                        value=opts.getThemeColor(opts.options.primaryHue).c500, show_label=False, scale=0)
                    self._components.primaryHue.change(
                        fn=lambda hue: opts.getThemeColor(hue).c500,
                        inputs=[self._components.primaryHue],
                        outputs=[primaryHuePreview],
                        show_progress='hidden',
                    )
                self._components.maxQueueSize = gr.Slider(value=opts.options.maxQueueSize, minimum=10, maximum=999, step=1,
                                                    show_reset_button=False, label="Max queue size")
                self._components.showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme (still functional when hidden)',
                                value=opts.options.showToggleDarkLightButton)
                self._components.showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI',
                                value=opts.options.showRunButtonCopy)

            applyChanges = ButtonWithConfirm("Apply changes", "Confirm apply", "Cancel")
            applyChanges.click(
                fn=self._onApplyChanges,
                inputs=list(self._components.values())
            )
