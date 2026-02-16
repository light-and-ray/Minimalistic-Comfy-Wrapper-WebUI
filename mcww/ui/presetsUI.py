import gradio as gr
import uuid, json
from dataclasses import dataclass
from mcww import shared
from mcww.presets import Presets
from mcww.ui.uiUtils import ButtonWithConfirm, showRenderingErrorGradio, JsonTextbox
from mcww.comfy.workflow import Element

PRESETS_FILTER_VISIBLE_THRESHOLD = 30

@dataclass
class PresetsUIState:
    textPromptElements: list[Element]
    workflowName: str
    selectedPreset: str = None


class PresetsUI:
    def __init__(self):
        self._buildPresetsUI()

    @staticmethod
    def getOnAddPreset(presets: Presets, promptComponentKeys: list[str]):
        def onAddPreset(newPresetName: str, *prompts):
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            if newPresetName == "+":
                raise gr.Error("New preset name can't be +", duration=1, print_exception=False)
            presets.addPresetName(newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Added "{newPresetName}"', 1)
        return onAddPreset


    @staticmethod
    def getOnDeletePreset(presets: Presets, presetName, state: PresetsUIState):
        def onDeletePreset():
            presets.deletePresetName(presetName)
            presets.save()
            gr.Info(f'Deleted "{presetName}"', 1)
            state.selectedPreset = None
            return state
        return onDeletePreset


    @staticmethod
    def getOnCleanupInvalidKeys(presets: Presets, presetName, invalidKeys: set[str]):
        def onCleanupInvalidKeys():
            for invalidKey in invalidKeys:
                presets.deleteKey(presetName, invalidKey)
            presets.save()
            gr.Info(f'Cleaned "{presetName}"', 1)
        return onCleanupInvalidKeys


    @staticmethod
    def getOnSaveCopyPreset(presets: Presets, promptComponentKeys: list[str], state: PresetsUIState):
        def onSaveCopyPreset(newPresetName: str, *prompts):
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            if newPresetName == "+":
                raise gr.Error("New preset name can't be +", duration=1, print_exception=False)
            presets.addPresetName(newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Saved "{newPresetName}"', 1)
            state.selectedPreset = newPresetName
            return state
        return onSaveCopyPreset


    @staticmethod
    def getOnSavePreset(presets: Presets, oldPresetName: str, promptComponentKeys: list[str], state: PresetsUIState):
        def onSavePreset(newPresetName: str, *prompts):
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            if newPresetName == "+":
                raise gr.Error("New preset name can't be +", duration=1, print_exception=False)
            presets.renamePreset(oldPresetName, newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Saved "{newPresetName}"', 1)
            state.selectedPreset = newPresetName
            return state
        return onSavePreset


    @staticmethod
    def onNewOrderAfterDragChange(newOrderJson: str, state: PresetsUIState|None):
        if not state:
            raise gr.Error("presetsUIState is None in onNewOrderAfterDragChange")
        newOrder: list[str] = json.loads(newOrderJson)
        newOrder.remove("+")
        presets = Presets(state.workflowName)
        presets.applyNewOrder(newOrder)
        presets.save()


    def _buildPresetsUI(self):
        with gr.Column() as self.ui:
            refreshPresetsTrigger = gr.Textbox(visible=False)
            refreshPresetsButton = gr.Button(elem_classes=["refresh-presets", "mcww-hidden"])
            refreshPresetsButton.click(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshPresetsTrigger],
            )

            newOrderAfterDrag = gr.Textbox(elem_classes=["mcww-hidden", "mcww-hidden-parent", "presets-new-order-after-drag"])
            newOrderAfterDrag.change(
                fn=self.onNewOrderAfterDragChange,
                inputs=[newOrderAfterDrag, shared.presetsUIStateComponent],
            ).then(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshPresetsTrigger],
            )

            @gr.render(
                triggers=[refreshPresetsTrigger.change],
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
                    selectedPreset = state.selectedPreset if state.selectedPreset else "+"
                    presetsRadio = gr.Radio(
                        choices=["+"] + presets.getPresetNames(), value=selectedPreset,
                        show_label=False, elem_classes=["mcww-presets-radio"])

                    @gr.on(
                        triggers=[presetsRadio.select],
                        inputs=[shared.presetsUIStateComponent, presetsRadio],
                        outputs=[shared.presetsUIStateComponent, refreshPresetsTrigger]
                    )
                    def onPresetSelected(state: PresetsUIState|None, selectedPreset: str):
                        if not state:
                            raise gr.Error("*** state is None in onPresetSelected")
                        state.selectedPreset = selectedPreset
                        return state, str(uuid.uuid4())

                    with gr.Column(elem_classes=["presets-editor-main-column"]):
                        if selectedPreset != "+":

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
                                    fn=self.getOnSavePreset(
                                        presets,
                                        selectedPreset,
                                        list(promptComponentByKey.keys()),
                                        state,
                                    ),
                                    inputs=[presetNameTextbox, *promptComponentByKey.values()],
                                    outputs=[shared.presetsUIStateComponent],
                                ).success(
                                    fn=lambda: [str(uuid.uuid4())],
                                    outputs=[refreshPresetsTrigger],
                                )
                                saveCopyButton = gr.Button("Save as copy")
                                saveCopyButton.click(
                                    fn=self.getOnSaveCopyPreset(
                                        presets,
                                        list(promptComponentByKey.keys()),
                                        state,
                                    ),
                                    inputs=[presetNameTextbox, *promptComponentByKey.values()],
                                    outputs=[shared.presetsUIStateComponent],
                                ).success(
                                    fn=lambda: [str(uuid.uuid4())],
                                    outputs=[refreshPresetsTrigger],
                                )
                                deleteButton = ButtonWithConfirm("Delete", "Confirm delete", "Cancel")
                                deleteButton.click(
                                    fn=self.getOnDeletePreset(presets, state.selectedPreset, state),
                                    outputs=[shared.presetsUIStateComponent],
                                ).success(
                                    fn=lambda: [str(uuid.uuid4())],
                                    outputs=[refreshPresetsTrigger],
                                )
                                if invalidKeys:
                                    cleanupButton = ButtonWithConfirm("Cleanup invalid keys", "Did you save?", "Cancel")
                                    cleanupButton.click(
                                        fn=self.getOnCleanupInvalidKeys(presets, state.selectedPreset, invalidKeys),
                                    ).success(
                                        fn=lambda: [str(uuid.uuid4())],
                                        outputs=[refreshPresetsTrigger],
                                    )
                        else:

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
                                    fn=self.getOnAddPreset(
                                        presets,
                                        list(promptComponentByKey.keys())
                                    ),
                                    inputs=[newPresetName, *promptComponentByKey.values()],
                                ).success(
                                    fn=lambda: [str(uuid.uuid4())],
                                    outputs=[refreshPresetsTrigger],
                                )
                        gr.Markdown("Use drag and drop to change presets order",
                            elem_classes=["mcww-visible", "info-text"])
                except Exception as e:
                    showRenderingErrorGradio(e, "On renderSelectedPreset")



def renderPresetsInWorkflowUI(workflowName: str, textPromptElementUiList: list):
    presets = Presets(workflowName)
    with gr.Column():
        elementKeys = [x.element.getKey() for x in textPromptElementUiList]
        elementComponents = [x.gradioComponent for x in textPromptElementUiList]
        presetsDataset = gr.Dataset( # gr.Examples apparently doesn't work in gr.render context
            sample_labels=presets.getPresetNames(),
            samples=presets.getPromptsInSamplesFormat(elementKeys),
            components=elementComponents,
            samples_per_page=9999999,
            show_label=False,
            elem_classes=["presets-dataset"],
        )
        presetsDataset.select(
            **shared.runJSFunctionKwargs("scrollToPresetsDataset.storePosition")
        ).then(
            fn=lambda x: (x if len(x) != 1 else x[0]),
            inputs=[presetsDataset],
            outputs=elementComponents,
        ).then(
            **shared.runJSFunctionKwargs("scrollToPresetsDataset.scrollToStoredPosition")
        )

        filterVisible = len(presets.getPresetNames()) > PRESETS_FILTER_VISIBLE_THRESHOLD
        filterComponent = gr.Textbox(label="Presets filter", elem_classes=["mcww-tiny-element", "presets-filter"], visible=filterVisible)

        editPresetsButton = gr.Button(
            "Edit presets",
            scale=0,
            elem_classes=["mcww-text-button", "edit-presets-button"])
        def onEditPresetsButton():
            return PresetsUIState(
                textPromptElements=[x.element for x in textPromptElementUiList],
                workflowName=workflowName,
            )
        editPresetsButton.click(
            fn=onEditPresetsButton,
            outputs=[shared.presetsUIStateComponent],
        ).then(
            **shared.runJSFunctionKwargs([
                "doSaveStates",
                "openPresetsPage",
            ])
        )

        def reloadPresetsFile():
            nonlocal presets
            presets = Presets(workflowName)

        def refreshPresetsDataset(filter):
            datasetUpdate = gr.Dataset(
                sample_labels=presets.getPresetNames(filter=filter),
                samples=presets.getPromptsInSamplesFormat(elementKeys, filter=filter),
            )
            if filter:
                filterVisible = True
            else:
                filterVisible = len(presets.getPresetNames()) > PRESETS_FILTER_VISIBLE_THRESHOLD
            filterUpdate = gr.Textbox(visible=filterVisible)
            return datasetUpdate, filterUpdate

        afterPresetsEditedButton = gr.Button(elem_classes=["mcww-hidden", "after-presets-edited"])
        refreshPresetsButton = gr.Button(elem_classes=["mcww-hidden", "refresh-presets-workflow-ui"])

        def attachRefreshDatasetListener(trigger, showProgress: bool, needReload: bool):
            if needReload:
                dependency = trigger(
                    fn=reloadPresetsFile,
                )
                trigger = dependency.then
            dependency = trigger(
                fn=refreshPresetsDataset,
                inputs=[filterComponent],
                outputs=[presetsDataset, filterComponent],
                show_progress='hidden' if not showProgress else 'minimal',
            ).then(
                **shared.runJSFunctionKwargs("calculatePresetDatasetHeights")
            )
            return dependency
        attachRefreshDatasetListener(afterPresetsEditedButton.click, showProgress=False, needReload=True)
        attachRefreshDatasetListener(filterComponent.change, showProgress=True, needReload=False)
        attachRefreshDatasetListener(refreshPresetsButton.click, showProgress=False, needReload=False)


