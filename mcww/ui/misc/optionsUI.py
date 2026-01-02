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
                    self._components.primaryHue = gr.Slider(label=f"Accent color hue", minimum=0, maximum=360, step=1)
                    primaryHuePreview = gr.ColorPicker(interactive=False, elem_classes=["accent-color-preview"],
                                        value=opts.getThemeColor(opts.options.primaryHue).c500, show_label=False, scale=0)
                    self._components.primaryHue.change(
                        fn=lambda hue: opts.getThemeColor(hue).c500,
                        inputs=[self._components.primaryHue],
                        outputs=[primaryHuePreview],
                        show_progress='hidden',
                    )
                self._components.maxQueueSize = gr.Slider(minimum=10, maximum=999, step=1, label="Max queue size")
                self._components.openAccordionsAutomatically = gr.Checkbox(label='Open accordions automatically (Advanced options and others)')
                self._components.showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme (still functional when hidden)')
                self._components.showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI')
                self._components.preventPullToRefreshGesture = gr.Checkbox(label="Prevent browser's pull to refresh gesture (on touchscreen)")

            for key, component in self._components.items():
                component.value = getattr(opts.options, key)
                if hasattr(component, 'show_reset_button'):
                    component.show_reset_button = False

            applyChanges = ButtonWithConfirm("Apply changes", "Confirm apply", "Cancel")
            applyChanges.click(
                fn=self._onApplyChanges,
                inputs=list(self._components.values())
            )
