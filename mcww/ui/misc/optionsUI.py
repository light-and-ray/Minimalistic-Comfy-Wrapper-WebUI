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
        with gr.Accordion("Detailed primary color settings", open=False, render=False) as accordion:
            with gr.Row(equal_height=True):
                with gr.Column(scale=2):
                    self._components.primaryHue = gr.Slider(label=f"Primary color hue", minimum=0, maximum=360, step=1)
                    self._components.primarySaturationList = gr.Textbox(label="Primary color saturation list")
                    self._components.primaryLightnessList = gr.Textbox(label="Primary color lightness list")
                with gr.Column(scale=3):
                    gr.Examples(list[list](opts.SL_PRESETS.values()), example_labels=list(opts.SL_PRESETS.keys()),
                        label="Saturation/Lightness presets", inputs=[self._components.primarySaturationList,
                        self._components.primaryLightnessList], elem_id='examples', examples_per_page=9999)
                    gr.Examples(list(opts.HUE_PRESETS.values()), examples_per_page=9999,
                        example_labels=list(opts.HUE_PRESETS.keys()),
                        inputs=[self._components.primaryHue], label="Hue presets", elem_id='examples')
        preview = gr.Image(format="png", show_label=False, show_download_button=False, show_fullscreen_button=False,
            elem_classes=["no-copy", "no-compare", "mcww-color-palette-preview", "no-pwa-context-menu"])
        gr.Examples(list[list](opts.FEATURED_COLORS.values()), example_labels=list(opts.FEATURED_COLORS.keys()),
            label="Primary color presets", inputs=[self._components.primaryHue, self._components.primarySaturationList,
            self._components.primaryLightnessList], elem_id='examples')
        accordion.render()
        def onThemePreviewUpdate(hue, saturationList, lightnessList):
            try:
                themeColor = opts.getThemeColor(hue, saturationList, lightnessList)
                hslStrings = [themeColor.c50, themeColor.c100, themeColor.c200, themeColor.c300, themeColor.c400,
                        themeColor.c500, themeColor.c600, themeColor.c700, themeColor.c800, themeColor.c900, themeColor.c950]
                palette = create_color_palette_image(hslStrings)
                return gr.Image(palette)
            except Exception:
                return gr.Image()
        gr.on(
            triggers=[
                self._components.primaryHue.change,
                self._components.primarySaturationList.change,
                self._components.primaryLightnessList.change,
            ],
            fn=onThemePreviewUpdate,
            inputs=[
                self._components.primaryHue,
                self._components.primarySaturationList,
                self._components.primaryLightnessList,
            ],
            outputs=preview,
            show_progress='hidden',
        )


    def _make_themeOptions(self):
        with gr.Column(elem_classes=["fix-background"]):
            with gr.Accordion(render=False, open=False, label="Detailed theme settings") as accordion:
                self._components.themeClass = gr.Radio(label="Theme class (buttons, labels etc)", choices=list[str](opts.THEME_CLASSES.keys()))
                self._components.secondaryColor = gr.Radio(label="Secondary color (progress bar, some focused elements)",
                            choices=list[str](opts.SECONDARY_COLORS.keys()))
                self._components.neutralColor = gr.Radio(label="Neutral color (background)",
                            choices=list[str](opts.NEUTRAL_COLORS.keys()))
                self._components.themeFlags = gr.CheckboxGroup(choices=opts.MCWW_THEME_FLAGS, label="MCWW theme flags (Flags for non-Gradio styles)")
            outputComponents = [self._components.themeClass, self._components.secondaryColor,
                self._components.neutralColor, self._components.themeFlags, self._components.primaryHue,
                self._components.primarySaturationList, self._components.primaryLightnessList]
            presets = gr.Dataset(samples=list[list](opts.FEATURED_THEMES.values()), sample_labels=list(opts.FEATURED_THEMES.keys()),
                label="Theme presets", components=outputComponents, elem_id='examples', samples_per_page=9999)
            accordion.render()
            with gr.Column(elem_classes=["themes-info"]):
                gr.Markdown(elem_classes=["mcww-visible", "themes-info", "allow-pwa-select"], value=
                    'Presets descriptions: \n'
                    '- **MCWW Flat**: The same as *Default*, but flat. Select this if you like the default theme, but dislike gray gradients \n'
                    '- **MCWW Rounded**: All elements are very rounded, gradients on buttons \n'
                    '- **MCWW Float**: This is a borderless theme with very bold labels. Light theme looks way more volumetric \n'
                    '- **MCWW Sharp**: All angles are 90° \n'
                    '- **Gradio Classic**: this theme you can know as A1111\'s default theme \n'
                    '- **Gradio Soft**: This theme is popular in many other UIs \n'
                    '- **Wan2GP**: The theme from Wan2GP UI \n'
                )
                gr.Markdown("Use any primary color for MCWW themes", elem_classes=["mcww-visible", "info-text"])
            def onThemePresetSelected(event: gr.SelectData):
                theme = event.value[0]
                results = copy.copy(opts.FEATURED_THEMES[theme])
                if theme in opts.FEATURED_THEMES_COLORS:
                    results += opts.FEATURED_THEMES_COLORS[theme]
                else:
                    results += [gr.update()] * 3
                gr.Info(f'Theme preset "{theme}" selected', 1)
                return results
            presets.select(
                fn=onThemePresetSelected,
                outputs=outputComponents,
            )


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
            with gr.Row(elem_classes=["floating-row", "right-aligned"], equal_height=True):
                refreshHiddenWorkflows = gr.Button("Refresh", elem_classes=["mcww-refresh", "small-button", "mcww-text-button"])
        gr.on(
            triggers=[shared.webUI.load, refreshHiddenWorkflows.click, shared.afterProjectRefreshedTrigger.change],
            fn=refreshHiddenWorkflowChoices,
            inputs=[self._components.hiddenWorkflows],
            outputs=[self._components.hiddenWorkflows],
        )


    def _buildOptionsUI(self):
        with gr.Column(elem_classes=["options-main-column"]) as self.ui:
            with gr.Tabs(elem_classes=["mcww-page-tabs"]):
                with gr.Tab("Queue"):
                    with gr.Group():
                        self._components.maxQueueSize = gr.Slider(minimum=10, maximum=999, step=1, label="Max queue size")
                        self._components.queueMaxPriority = gr.Slider(minimum=1, maximum=9, step=1, label="Max queue priority")
                        self._make_defaultPriority()
                with gr.Tab("Behavior"):
                    with gr.Group():
                        self._components.openAccordionsAutomatically = gr.Checkbox(label='Open accordions automatically (Advanced options and others)')
                        self._components.hideSidebarByDefault = gr.Checkbox(label="Hide sidebar by default (desktop layout)")
                        self._components.autoRefreshPageOnBackendRestarted = gr.Checkbox(label="Automatically refresh page after backend restarted instead of showing a toasted message")
                        self._components.mirrorWebCamera = gr.Checkbox(label="Mirror camera inside image and video input components")
                        self._components.defaultVideosVolume = gr.Slider(minimum=0.0, maximum=1.0, step=0.01, label="Initial video volume in galleries")
                        self._components.presetsFilterThreshold = gr.Slider(minimum=2, maximum=100, step=1, label="Presets filter appear threshold")
                        self._make_hiddenWorkflows()
                with gr.Tab("Layout"):
                    with gr.Group():
                        self._components.showRunButtonCopy = gr.Checkbox(label='Show non-floating run button in workflow UI')
                        self._components.forceShowBatchCount = gr.Checkbox(label='Show "Batch count" parameter even if workflow doesn\'t have any seeds')
                        self._components.hideHomepagesInFooter = gr.Checkbox(label='Hide homepage links in the footer (MCWW, Gradio, ComfyUI)')
                        self._components.showToggleDarkLightButton = gr.Checkbox(label='Show "☀️/🌙" button for changing dark/light theme (still functional when hidden)')
                        self._components.useCustomContextMenu = gr.Checkbox(label="Use custom context menu instead of browser's context menu. (Everything except text boxes)")
                with gr.Tab("Theme"):
                    with gr.Group():
                        self._make_primaryColorOptions()
                    with gr.Group():
                        self._make_themeOptions()
                    with gr.Group():
                        self._components.preferredThemeDarkLight = gr.Radio(choices=["System", "Dark", "Light"], label="Preferred theme Dark/Light")

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
            gr.Markdown("Apply and Discard do the action on all the tabs simultaneously", elem_classes=["mcww-visible", "info-text"])
