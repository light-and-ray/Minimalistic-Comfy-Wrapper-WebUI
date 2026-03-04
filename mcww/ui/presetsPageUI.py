import gradio as gr
import uuid
from mcww import shared, opts
from mcww.presets import Presets
from mcww.ui.uiUtils import ButtonWithConfirm, showRenderingErrorGradio, JsonTextbox
from mcww.ui.presetsUIUtils import PresetsUiActions, PresetsUIState


class PresetsUI:
    def __init__(self):
        self._buildPresetsUI()

    def _buildEditOnePresetUI(self, selectedPreset: str, presets: Presets, state: PresetsUIState):
        presetNameTextbox = gr.Textbox(
            value=selectedPreset,
            label="Preset name",
            lines=1,
            max_lines=1,
            elem_classes=["mcww-bold-label"],
        )
        promptComponentByKey = dict[str, gr.Textbox]()
        validKeys = set[str]()
        for element in state.textPromptElements:
            key = element.getKey()
            validKeys.add(key)
            if element.isJson():
                textboxClass = JsonTextbox
            else:
                textboxClass = gr.Textbox
            promptComponentByKey[key] = textboxClass(
                show_label=False,
                info=element.label,
                value=presets.getPromptValue(selectedPreset, key),
                lines=2,
            )
        invalidKeys = set[str]()
        for key in presets.getAllKeys(selectedPreset):
            if key in validKeys: continue
            invalidKeys.add(key)
            gr.Textbox(
                label=f"Invalid: {key}",
                info=f"Invalid key is found in preset json. This sometime can happen after workflow change. Copy them and save for recovery",
                value=presets.getPromptValue(selectedPreset, key),
                lines=2,
                interactive=False
            )
        with gr.Row():
            savePresetButton = gr.Button("Save", elem_classes=["mcww-save-button"])
            savePresetButton.click(
                fn=PresetsUiActions.getOnSavePreset(
                    presets,
                    selectedPreset,
                    list(promptComponentByKey.keys()),
                    state,
                ),
                inputs=[presetNameTextbox, *promptComponentByKey.values()],
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )
            saveCopyButton = gr.Button("Save as copy")
            saveCopyButton.click(
                fn=PresetsUiActions.getOnSaveCopyPreset(
                    presets,
                    list(promptComponentByKey.keys()),
                    state,
                ),
                inputs=[presetNameTextbox, *promptComponentByKey.values()],
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )
            deleteButton = ButtonWithConfirm("Delete", "Confirm delete", "Cancel")
            deleteButton.click(
                fn=PresetsUiActions.getOnDeletePreset(presets, state.selectedPreset, state),
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )
            if invalidKeys:
                cleanupButton = ButtonWithConfirm("Cleanup invalid keys", "Did you save?", "Cancel")
                cleanupButton.click(
                    fn=PresetsUiActions.getOnCleanupInvalidKeys(presets, state.selectedPreset, invalidKeys),
                ).success(
                    fn=lambda: [str(uuid.uuid4())],
                    outputs=[self.refreshPresetsTrigger],
                )


    def _buildEditFilterUI(self, selectedFilter: str, presets: Presets, state: PresetsUIState):
        filterNameTextbox = gr.Textbox(
            value=selectedFilter.removeprefix("⌕ "),
            label="Filter name",
            lines=1,
            max_lines=1,
            elem_classes=["mcww-bold-label"],
        )
        filterValue = gr.Textbox(
            show_label=False,
            info="Presets filter",
            value=presets.getPromptValue(selectedFilter, Presets.SAVED_FILTER_ELEMENT_KEY),
            lines=2,
        )
        with gr.Row():
            savePresetButton = gr.Button("Save", elem_classes=["mcww-save-button"])
            savePresetButton.click(
                fn=PresetsUiActions.getOnSavePreset(
                    presets,
                    selectedFilter,
                    [Presets.SAVED_FILTER_ELEMENT_KEY],
                    state,
                ),
                inputs=[filterNameTextbox, filterValue],
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )
            saveCopyButton = gr.Button("Save as copy")
            saveCopyButton.click(
                fn=PresetsUiActions.getOnSaveCopyPreset(
                    presets,
                    [Presets.SAVED_FILTER_ELEMENT_KEY],
                    state,
                ),
                inputs=[filterNameTextbox, filterValue],
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )
            deleteButton = ButtonWithConfirm("Delete", "Confirm delete", "Cancel")
            deleteButton.click(
                fn=PresetsUiActions.getOnDeletePreset(presets, state.selectedPreset, state),
                outputs=[shared.presetsUIStateComponent],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )


    def _buildAddPresetUI(self, presets: Presets, state: PresetsUIState):
        newPresetName = gr.Textbox(label="New preset name", elem_classes=["mcww-bold-label"])
        promptComponentByKey = dict[str, gr.Textbox]()
        for element in state.textPromptElements:
            if element.isJson():
                textboxClass = JsonTextbox
            else:
                textboxClass = gr.Textbox
            key = element.getKey()
            promptComponentByKey[key] = textboxClass(
                show_label=False,
                info=element.label,
                value="",
                lines=2,
            )
        with gr.Row():
            addPresetButton = gr.Button("Add new preset", elem_classes=["mcww-save-button"])
            addPresetButton.click(
                fn=PresetsUiActions.getOnAddPreset(
                    presets,
                    list(promptComponentByKey.keys())
                ),
                inputs=[newPresetName, *promptComponentByKey.values()],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )


    def _buildAddFilterUI(self, presets: Presets, state: PresetsUIState):
        newFilterName = gr.Textbox(label="New filter name", elem_classes=["mcww-bold-label"])
        newFilterValue = gr.Textbox(
            show_label=False,
            info="Presets filter",
            value="",
            lines=2,
        )
        with gr.Row():
            addFilterButton = gr.Button("Add new filter", elem_classes=["mcww-save-button"])
            addFilterButton.click(
                fn=PresetsUiActions.getOnAddPreset(
                    presets,
                    [Presets.SAVED_FILTER_ELEMENT_KEY]
                ),
                inputs=[newFilterName, newFilterValue],
            ).success(
                fn=lambda: [str(uuid.uuid4())],
                outputs=[self.refreshPresetsTrigger],
            )


    def _buildPresetsUI(self):
        with gr.Column() as self.ui:
            self.refreshPresetsTrigger = gr.Textbox(visible=False)
            refreshPresetsButton = gr.Button(elem_classes=["refresh-presets", "mcww-hidden"])
            refreshPresetsButton.click(
                fn=lambda: str(uuid.uuid4()),
                outputs=[self.refreshPresetsTrigger],
            )

            newOrderAfterDrag = gr.Textbox(elem_classes=["mcww-hidden", "mcww-hidden-parent", "presets-new-order-after-drag"])
            newOrderAfterDrag.change(
                fn=PresetsUiActions.onNewOrderAfterDragChange,
                inputs=[newOrderAfterDrag, shared.presetsUIStateComponent],
            ).then(
                fn=lambda: str(uuid.uuid4()),
                outputs=[self.refreshPresetsTrigger],
            )

            @gr.render(
                triggers=[self.refreshPresetsTrigger.change],
                inputs=[shared.presetsUIStateComponent],
            )
            def renderSelectedPreset(state: PresetsUIState|None):
                try:
                    if not state:
                        gr.Markdown("presetsUIState is None in renderSelectedPreset", elem_classes=["mcww-visible"])
                        return
                    if not state.selectedPreset:
                        state.selectedPreset = "+"
                    presets = Presets(state.workflowName)

                    with gr.Row(equal_height=True):
                        backButton = gr.Button("🡠", elem_classes=["mcww-tool"], scale=0)
                        backButton.click(
                            **shared.runJSFunctionKwargs("goBack")
                        )
                        gr.Markdown(f'## Presets editor for "{state.workflowName}"',
                                            elem_classes=["mcww-visible", "presets-title"])
                    needFilter = len(presets.getPresetNames()) >= opts.options.presetsFilterThreshold
                    selectedPreset = state.selectedPreset if state.selectedPreset else "+"
                    addChoices = ["+"]
                    if needFilter:
                        addChoices += ["+⌕"]
                    presetsRadio = gr.Radio(
                        choices=addChoices + presets.getPresetAndSavedFiltersNames(), value=selectedPreset,
                        show_label=False, elem_classes=["mcww-presets-radio"])

                    @gr.on(
                        triggers=[presetsRadio.select],
                        inputs=[shared.presetsUIStateComponent, presetsRadio],
                        outputs=[shared.presetsUIStateComponent, self.refreshPresetsTrigger]
                    )
                    def onPresetSelected(state: PresetsUIState|None, selectedPreset: str):
                        if not state:
                            raise gr.Error("*** state is None in onPresetSelected")
                        state.selectedPreset = selectedPreset
                        return state, str(uuid.uuid4())

                    with gr.Column(elem_classes=["presets-editor-main-column"]):
                        if selectedPreset == "+":
                            self._buildAddPresetUI(presets, state)
                        elif selectedPreset == "+⌕":
                            self._buildAddFilterUI(presets, state)
                        else:
                            if Presets.SAVED_FILTER_ELEMENT_KEY not in presets.getAllKeys(selectedPreset):
                                self._buildEditOnePresetUI(selectedPreset, presets, state)
                            else:
                                self._buildEditFilterUI(selectedPreset, presets, state)
                        gr.Markdown("Use drag and drop to change presets order",
                            elem_classes=["mcww-visible", "info-text"])
                except Exception as e:
                    showRenderingErrorGradio(e, "On renderSelectedPreset")

