import gradio as gr
import copy
from wrapt import synchronized
from mcww import opts, shared
from mcww.utils import AttrDict
from mcww.ui.uiUtils import ButtonWithConfirm, create_color_palette_image
from mcww.ui.misc.management import restartComfy, restartStandalone


class OptionsUI:
    def __init__(self):
        self._components = AttrDict()
        self._buildOptionsUI()


    @synchronized
    def _onDiscardChanges(self):
        values = []
        for key in self._components.keys():
            values.append(getattr(opts.options, key))
        return values

    @synchronized
    def _onApplyChanges(self, *args):
        for key, value in zip(self._components.keys(), args):
            setattr(opts.options, key, value)
        opts.saveOptions()
        gr.Info("Options saved, restart UI to apply some of them", 4)

    def _make_primaryColorOptions(self):
        with gr.Row(equal_height=True):
            self._components.primaryHue = gr.Slider(label=f"Accent color hue", minimum=0, maximum=360, step=1)
            preview = gr.Image(format="png", show_label=False, show_download_button=False, show_fullscreen_button=False,
                elem_classes=["no-copy", "no-compare", "mcww-color-palette"])
        with gr.Row(equal_height=True):
            with gr.Column():
                self._components.primarySaturationList = gr.Textbox(label="Accent color saturation list")
                self._components.primaryLuminanceList = gr.Textbox(label="Accent color luminance list")
            with gr.Column():
                gr.Examples([25, 54, 100, 145, 169, 181, 218, 274, 288, 326, 360], examples_per_page=9999,
                    example_labels=["Orange", "Yellow", "Green", "Mint", "Turquoise", "Cyan", "Blue", "Violet", "Purple", "Magenta", "Red"],
                    inputs=[self._components.primaryHue], label="Hue presets", elem_id='accentColorExamples')
                gr.Examples([
                    ['[85, 85, 55, 33, 24, 18, 18, 14, 14, 13, 13]', '[100, 95, 89, 82, 75, 69, 61, 53, 43, 39, 34]'],
                    ['[85, 85, 80, 75, 73, 69, 65, 60, 60, 55, 50]', '[91, 88, 85, 82, 80, 78, 75, 72, 68, 65, 60]'],
                    ['[100, 100, 100, 97, 96, 95, 90, 88, 79, 75, 71]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
                    ['[65, 55, 39, 29, 36, 38, 43, 43, 44, 44, 50]', '[88, 80, 72, 62, 51, 40, 30, 20, 13, 10, 8]'],
                    ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[95, 90, 88, 85, 83, 80, 77, 75, 70, 68, 65]'],
                    ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[96, 92, 85, 72, 61, 53, 48, 40, 34, 28, 25]'],
                    ['[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[88, 80, 72, 62, 51, 40, 30, 20, 13, 10, 8]'],
                ], example_labels=["Dusty", "Pastel", "Vibrant", "Dark", "Gray L", "Gray N", "Gray D"], label="Saturation/Luminance presets",
                inputs=[self._components.primarySaturationList, self._components.primaryLuminanceList], elem_id='accentColorExamples')
        @gr.on(
            triggers=[
                self._components.primaryHue.change,
                self._components.primarySaturationList.change,
                self._components.primaryLuminanceList.change,
            ],
            inputs=[
                self._components.primaryHue,
                self._components.primarySaturationList,
                self._components.primaryLuminanceList,
            ],
            outputs=preview,
            show_progress='hidden',
        )
        def onThemePreviewUpdate(hue, saturationList, lumaList):
            try:
                themeColor = opts.getThemeColor(hue, saturationList, lumaList)
                hslStrings = [themeColor.c50, themeColor.c100, themeColor.c200, themeColor.c300, themeColor.c400,
                            themeColor.c500, themeColor.c600, themeColor.c700, themeColor.c800, themeColor.c900, themeColor.c950]
                palette = create_color_palette_image(hslStrings)
                return gr.Image(palette)
            except Exception:
                return gr.Image()



    def _make_defaultPriority(self):
        choices=list[int](range(1, opts.options.queueMaxPriority+1))
        self._components.defaultPriority = gr.Radio(label="Default priority for newly opened workflows", choices=choices)
        def refreshDefaultPriorityChoices(maxPriority: int, defaultPriority: int):
            if not maxPriority or not defaultPriority:
                return gr.Radio()
            choices = list[int](range(1, maxPriority+1))
            return gr.Radio(choices=choices, value=min(maxPriority, defaultPriority))
        self._components.queueMaxPriority.change(
            fn=refreshDefaultPriorityChoices,
            inputs=[self._components.queueMaxPriority, self._components.defaultPriority],
            outputs=[self._components.defaultPriority],
            show_progress='hidden',
        )


    def _make_hiddenWorkflows(self):
        def refreshHiddenWorkflowChoices(values: list[str]):
            choices = copy.copy(values)
            try:
                for workflowName in shared.projectUI.getWorkflows().keys():
                    if workflowName not in choices:
                        choices.append(workflowName)
            except Exception:
                pass
            return gr.Dropdown(choices=choices)
        with gr.Row():
            self._components.hiddenWorkflows = gr.Dropdown(label="Hide workflows (wildcards supported, case sensitive, only file name, no .json extension)",
                                                    multiselect=True, allow_custom_value=True)
            refreshHiddenWorkflows = gr.Button("Refresh", elem_classes=["mcww-refresh", "mcww-text-button"])
        gr.on(
            triggers=[shared.webUI.load, refreshHiddenWorkflows.click, shared.refreshProjectTrigger.change],
            fn=refreshHiddenWorkflowChoices,
            inputs=[self._components.hiddenWorkflows],
            outputs=[self._components.hiddenWorkflows],
        )


    def _buildOptionsUI(self):
        with gr.Column(elem_classes=["options-main-column"]) as self.ui:
            with gr.Group():
                self._make_primaryColorOptions()
                self._components.maxQueueSize = gr.Slider(minimum=10, maximum=999, step=1, label="Max queue size")
                self._components.queueMaxPriority = gr.Slider(minimum=1, maximum=9, step=1, label="Max queue priority")
                self._make_defaultPriority()
                self._components.openAccordionsAutomatically = gr.Checkbox(label='Open accordions automatically (Advanced options and others)')
                self._components.hideSidebarByDefault = gr.Checkbox(label="Hide sidebar by default (desktop layout)")
                self._components.showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme (still functional when hidden)')
                self._components.showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI')
                self._components.autoRefreshPageOnBackendRestarted = gr.Checkbox(label="Automatically refresh page after backend restarted instead of showing a toasted message")
                self._components.defaultVideosVolume = gr.Slider(minimum=0.0, maximum=1.0, step=0.01, label="Initial video volume in galleries")
                self._components.mirrorWebCamera = gr.Checkbox(label="Mirror camera inside image and video input components")
                self._make_hiddenWorkflows()
                self._components.forceShowBatchCount = gr.Checkbox(label='Show "Batch count" parameter even if workflow doesn\'t have any seeds')
                self._components.hideHomepagesInFooter = gr.Checkbox(label='Hide homepage links in the footer (MCWW, Gradio, ComfyUI)')

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
