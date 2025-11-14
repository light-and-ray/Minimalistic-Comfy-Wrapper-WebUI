import gradio as gr
import uuid
from dataclasses import dataclass
from mcww import shared, opts
from mcww.presets import Presets
from mcww.ui.uiUtils import ButtonWithConfirm
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcww.ui.workflowUI import ElementUI


@dataclass
class PresetsUIState:
    textPromptElementsUI: list['ElementUI']
    workflowName: str
    selectedPreset: str = None


class PresetsUI:
    def __init__(self):
        self._buildPresetsUI()

    @staticmethod
    def getOnAddPreset(presets: Presets, promptComponentKeys: list[str]):
        def onAddPreset(newPresetName: str, *prompts):
            newPresetName = newPresetName.strip()
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            presets.addPresetName(newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Added "{newPresetName}"', 1)
        return onAddPreset


    @staticmethod
    def getOnDeletePreset(presets: Presets, presetName):
        def onDeletePreset():
            presets.deletePresetName(presetName)
            presets.save()
            gr.Info(f'Deleted "{presetName}"', 1)
        return onDeletePreset


    @staticmethod
    def afterPresetDeleted(state: PresetsUIState|None):
        if not state:
            gr.Markdown("presetsUIState is None in afterPresetDeleted", elem_classes=["mcww-visible"])
            return gr.State()
        state.selectedPreset = None
        return state


    @staticmethod
    def getOnSaveCopyPreset(presets: Presets, promptComponentKeys: list[str]):
        def onSaveCopyPreset(newPresetName: str, *prompts):
            newPresetName = newPresetName.strip()
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            presets.addPresetName(newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Saved "{newPresetName}"', 1)
        return onSaveCopyPreset


    @staticmethod
    def afterCopySaved(newPresetName: str, state: PresetsUIState|None):
        if not state:
            gr.Markdown("presetsUIState is None in afterCopySaved", elem_classes=["mcww-visible"])
            return gr.State()
        state.selectedPreset = newPresetName
        return state


    @staticmethod
    def getOnSavePreset(presets: Presets, oldPresetName: str, promptComponentKeys: list[str]):
        def onSavePreset(newPresetName: str, *prompts):
            newPresetName = newPresetName.strip()
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            presets.renamePreset(oldPresetName, newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            presets.save()
            gr.Info(f'Saved "{newPresetName}"', 1)
        return onSavePreset


    @staticmethod
    def getOnMoveUp(presets: Presets, presetName):
        def onMoveUp():
            presets.moveUp(presetName)
            presets.save()
        return onMoveUp


    @staticmethod
    def getOnMoveDown(presets: Presets, presetName):
        def onMoveDown():
            presets.moveDown(presetName)
            presets.save()
        return onMoveDown


    def _buildPresetsUI(self):
        with gr.Column(visible=False) as self.ui:
            refreshPresetsTrigger = gr.Textbox(visible=False)
            refreshPresetsButton = gr.Button(elem_classes=["refresh-presets", "mcww-hidden"])
            refreshPresetsButton.click(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshPresetsTrigger],
            )
            refreshSelectedPresetTrigger = gr.Textbox(visible=False)


            with gr.Row(equal_height=True):
                backButton = gr.Button("🡠", elem_classes=["mcww-tool"], scale=0)
                backButton.click(
                    **shared.runJSFunctionKwargs("goBack")
                )
                titleMarkdown = gr.Markdown(elem_classes=["mcww-visible", "presets-title"])

            presetsDataset = gr.Dataset(
                sample_labels=[], samples=[], show_label=False,
                components=[], samples_per_page=opts.presetsPerPageInEditor,
            )

            @gr.on(
                triggers=[refreshPresetsTrigger.change],
                inputs=[shared.presetsUIStateComponent],
                outputs=[presetsDataset, titleMarkdown, refreshSelectedPresetTrigger],
                show_progress='hidden',
            )
            def onPresetsRefresh(state: PresetsUIState|None):
                if not state:
                    print("*** state is None in onPresetsRefresh")
                    return gr.Dataset(), gr.Markdown(), gr.Textbox()
                presets = Presets(state.workflowName)

                sample_labels = presets.getPresetNames()
                samples = [[x] for x in presets.getPresetNames()]
                components = [shared.dummyComponent]
                sample_labels = ["+"] + sample_labels
                samples = [["+"]] + samples

                datasetUpdate = gr.Dataset(
                    sample_labels=sample_labels,
                    samples=samples,
                    components=components,
                )

                markdownUpdate = gr.Markdown(f'## Presets editor for "{state.workflowName}"')

                return datasetUpdate, markdownUpdate, str(uuid.uuid4())

            @gr.on(
                triggers=[presetsDataset.select],
                inputs=[shared.presetsUIStateComponent, presetsDataset],
                outputs=[shared.presetsUIStateComponent, refreshSelectedPresetTrigger]
            )
            def onPresetSelected(state: PresetsUIState|None, selectedPreset: str):
                if not state or not selectedPreset:
                    print("*** state is None in onPresetSelected")
                    return gr.Textbox()
                state.selectedPreset = selectedPreset[0]
                return state, str(uuid.uuid4())

            @gr.render(
                triggers=[refreshSelectedPresetTrigger.change],
                inputs=[shared.presetsUIStateComponent],
            )
            def renderSelectedPreset(state: PresetsUIState|None):
                if not state:
                    gr.Markdown("presetsUIState is None in renderSelectedPreset", elem_classes=["mcww-visible"])
                    return
                if not state.selectedPreset:
                    state.selectedPreset = "+"
                presets = Presets(state.workflowName)

                with gr.Column(elem_classes=["presets-editor-main-column"]):
                    if state.selectedPreset != "+":

                        with gr.Row(elem_classes=["presets-arrows-row"]):
                            moveUpButton = gr.Button("🡐", elem_classes=["mcww-tool", "mcww-text-button"], scale=0)
                            moveUpButton.click(
                                fn=self.getOnMoveUp(presets, state.selectedPreset),
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )
                            moveDownButton = gr.Button("🡒", elem_classes=["mcww-tool", "mcww-text-button"], scale=0)
                            moveDownButton.click(
                                fn=self.getOnMoveDown(presets, state.selectedPreset),
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )
                        presetNameTextbox = gr.Textbox(
                            value=state.selectedPreset,
                            label="Preset name",
                            lines=1,
                            max_lines=1,
                            elem_classes=["mcww-bold-label"],
                        )
                        promptComponentByKey = dict[str, gr.Textbox]()
                        for element in [x.element for x in state.textPromptElementsUI]:
                            key = element.getKey()
                            promptComponentByKey[key] = gr.Textbox(
                                show_label=False,
                                info=element.label,
                                value=presets.getPromptValue(state.selectedPreset, key),
                                lines=2,
                            )
                        with gr.Row():
                            savePresetButton = gr.Button("Save")
                            savePresetButton.click(
                                fn=self.getOnSavePreset(
                                    presets,
                                    state.selectedPreset,
                                    list(promptComponentByKey.keys())
                                ),
                                inputs=[presetNameTextbox, *promptComponentByKey.values()],
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )
                            saveCopyButton = gr.Button("Save (copy)")
                            saveCopyButton.click(
                                fn=self.getOnSaveCopyPreset(
                                    presets,
                                    list(promptComponentByKey.keys())
                                ),
                                inputs=[presetNameTextbox, *promptComponentByKey.values()],
                            ).then(
                                fn=self.afterCopySaved,
                                inputs=[presetNameTextbox, shared.presetsUIStateComponent],
                                outputs=[shared.presetsUIStateComponent],
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )
                            deleteButton = ButtonWithConfirm("Delete", "Confirm delete", "Cancel")
                            deleteButton.click(
                                fn=self.getOnDeletePreset(presets, state.selectedPreset),
                            ).then(
                                fn=self.afterPresetDeleted,
                                inputs=[shared.presetsUIStateComponent],
                                outputs=[shared.presetsUIStateComponent],
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )

                    else:

                        newPresetName = gr.Textbox(label="New preset name", elem_classes=["mcww-bold-label"])
                        promptComponentByKey = dict[str, gr.Textbox]()
                        for element in [x.element for x in state.textPromptElementsUI]:
                            key = element.getKey()
                            promptComponentByKey[key] = gr.Textbox(
                                show_label=False,
                                info=element.label,
                                value="",
                                lines=2,
                            )
                        with gr.Row():
                            addPresetButton = gr.Button("Add new preset")
                            addPresetButton.click(
                                fn=self.getOnAddPreset(
                                    presets,
                                    list(promptComponentByKey.keys())
                                ),
                                inputs=[newPresetName, *promptComponentByKey.values()],
                            ).then(
                                fn=lambda: [str(uuid.uuid4())],
                                outputs=[refreshPresetsTrigger],
                            )


def renderPresetsInWorkflowUI(workflowName: str, textPromptElementUiList: list):
    presets = Presets(workflowName)
    with gr.Column():
        elementKeys = [x.element.getKey() for x in textPromptElementUiList]
        elementComponents = [x.gradioComponent for x in textPromptElementUiList]
        presetsDataset = gr.Dataset( # gr.Examples apparently doesn't work in gr.render context
            sample_labels=presets.getPresetNames(),
            samples=presets.getPromptsInSamplesFormat(elementKeys),
            components=elementComponents,
            samples_per_page=opts.presetsPerPage,
            show_label=False,
            visible=bool(presets.getPresetNames()),
        )
        presetsDataset.select(
            fn=lambda x: (x if len(x) != 1 else x[0]),
            inputs=[presetsDataset],
            outputs=elementComponents,
        )

        editPresetsButton = gr.Button(
            "Edit presets",
            scale=0,
            elem_classes=["mcww-text-button", "edit-presets-button"])
        def onEditPresetsButton():
            return PresetsUIState(
                textPromptElementsUI=textPromptElementUiList,
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

        afterPresetsEditedButton = gr.Button(
            elem_classes=["mcww-hidden", "after-presets-edited"])
        def afterPresetsEdited():
            presets = Presets(workflowName)
            datasetUpdate = gr.Dataset(
                sample_labels=presets.getPresetNames(),
                samples=presets.getPromptsInSamplesFormat(elementKeys),
                visible=bool(presets.getPresetNames()),
            )
            return datasetUpdate
        afterPresetsEditedButton.click(
            fn=afterPresetsEdited,
            outputs=[presetsDataset]
        )

