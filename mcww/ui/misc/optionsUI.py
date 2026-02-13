import gradio as gr
import copy
from mcww import opts, shared
from mcww.utils import AttrDict
from mcww.ui.uiUtils import ButtonWithConfirm
from mcww.ui.misc.management import restartComfy, restartStandalone


class OptionsUI:
    def __init__(self):
        self._components = AttrDict()
        self._buildOptionsUI()


    def _onDiscardChanges(self):
        values = []
        for key in self._components.keys():
            values.append(getattr(opts.options, key))
        return values


    def _onApplyChanges(self, *args):
        for key, value in zip(self._components.keys(), args):
            setattr(opts.options, key, value)
        opts.saveOptions()
        gr.Info("Options saved, restart UI to apply some of them", 4)


    def _buildOptionsUI(self):
        with gr.Column(elem_classes=["options-main-column"]) as self.ui:
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
                    gr.Examples([54, 145, 218, 274, 355], inputs=[self._components.primaryHue], label="Hue presets", elem_id='accentColorExamples')
                self._components.maxQueueSize = gr.Slider(minimum=10, maximum=999, step=1, label="Max queue size")
                self._components.openAccordionsAutomatically = gr.Checkbox(label='Open accordions automatically (Advanced options and others)')
                self._components.hideSidebarByDefault = gr.Checkbox(label="Hide sidebar by default (desktop layout)")
                self._components.showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme (still functional when hidden)')
                self._components.showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI')
                self._components.autoRefreshPageOnBackendRestarted = gr.Checkbox(label="Automatically refresh page after backend restarted instead of showing a toasted message")
                self._components.defaultVideosVolume = gr.Slider(minimum=0.0, maximum=1.0, step=0.01, label="Default volume in video components")
                self._components.mirrorWebCamera = gr.Checkbox(label="Mirror camera inside image and video input components")
                def refreshHiddenWorkflowChoices():
                    choices = copy.copy(opts.options.hiddenWorkflows)
                    try:
                        for workflowName in shared.projectUI.getWorkflows().keys():
                            if workflowName not in choices:
                                choices.append(workflowName)
                    except Exception:
                        pass
                    return gr.Dropdown(choices=choices)
                with gr.Row():
                    self._components.hiddenWorkflows = gr.Dropdown(label="Hide workflows", multiselect=True, allow_custom_value=True)
                    refreshHiddenWorkflows = gr.Button("Refresh", elem_classes=["mcww-refresh", "mcww-text-button"])
                gr.on(
                    triggers=[shared.webUI.load, refreshHiddenWorkflows.click, shared.refreshProjectTrigger.change],
                    fn=refreshHiddenWorkflowChoices,
                    outputs=[self._components.hiddenWorkflows],
                )

            for component in self._components.values():
                if hasattr(component, 'show_reset_button'):
                    component.show_reset_button = False

            applyChanges = ButtonWithConfirm("Apply changes", "Confirm apply", "Cancel")
            applyChanges.click(
                fn=self._onApplyChanges,
                inputs=list(self._components.values())
            )
            if opts.IS_STANDALONE:
                restartButton = ButtonWithConfirm("Restart this WebUI", "Confirm restart", "Cancel")
                restartButton.click(
                    fn=restartStandalone,
                )
            else:
                restartButton = ButtonWithConfirm("Restart Comfy", "Confirm restart", "Cancel")
                restartButton.click(
                    fn=restartComfy,
                )
            discardChanges = gr.Button("Discard changes")
            gr.on(
                triggers=[discardChanges.click, shared.webUI.load],
                fn=self._onDiscardChanges,
                outputs=list(self._components.values())
            )
