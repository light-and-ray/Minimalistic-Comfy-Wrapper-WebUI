import gradio as gr
import uuid
from dataclasses import dataclass
from mcww import shared
from mcww.presets import Presets
from mcww.ui.uiUtils import ButtonWithConfirm
from mcww.comfy.workflow import Element


@dataclass
class PresetsUIState:
    textPromptElements: list[Element]
    workflowName: str


class PresetsUI:
    def __init__(self):
        self._buildPresetsUI()

    @staticmethod
    def getOnAddPreset(presets: Presets):
        def onAddPreset(newName: str):
            newName = newName.strip()
            if not newName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            presets.addPresetName(newName)
            gr.Info(f'Added "{newName}"', 1)
        return onAddPreset


    @staticmethod
    def getOnDeletePreset(presets: Presets, presetName):
        def onDeletePreset():
            presets.deletePresetName(presetName)
            gr.Info(f'Deleted "{presetName}"', 1)
        return onDeletePreset


    @staticmethod
    def getOnSavePreset(presets: Presets, oldPresetName: str, promptComponentKeys: list[str]):
        def onSavePreset(newPresetName, *prompts):
            presets.renamePreset(oldPresetName, newPresetName)
            for elementKey, promptValue in zip(promptComponentKeys, prompts):
                presets.setPromptValue(newPresetName, elementKey, promptValue)
            gr.Info(f'Saved "{newPresetName}"', 1)
        return onSavePreset


    def _buildPresetsUI(self):
        refreshPresetsTrigger = gr.Textbox(visible=False)

        with gr.Column(visible=False) as self.ui:
            @gr.render(
                triggers=[refreshPresetsTrigger.change],
                inputs=[shared.presetsUIStateComponent],
            )
            def renderPresets(state: PresetsUIState|None):
                if not state:
                    gr.Markdown("presetsUIState is None", elem_classes=["mcww-visible"])
                    return
                presets = Presets(state.workflowName)

                with gr.Row(equal_height=True):
                    backButton = gr.Button("🡠", elem_classes=["mcww-tool"], scale=0)
                    backButton.click(
                        **shared.runJSFunctionKwargs("goBack")
                    )
                    gr.Markdown(f"## Presets editor for `{state.workflowName}`", elem_classes=["mcww-visible"])
                with gr.Row():
                    newPresetName = gr.Textbox(label="New preset name")
                    addPresetButton = gr.Button("Add new preset")
                    addPresetButton.click(
                        fn=self.getOnAddPreset(presets),
                        inputs=[newPresetName],
                    ).then(
                        fn=lambda: [str(uuid.uuid4()), ""],
                        outputs=[refreshPresetsTrigger, newPresetName],
                    )

                for presetName in presets.getPresetNames():
                    with gr.Row():
                        promptComponentByKey = dict[str, gr.Textbox]()
                        with gr.Column(scale=10):
                            presetNameTextbox = gr.Textbox(
                                value=presetName,
                                label="Preset name",
                                lines=1,
                                max_lines=1
                            )
                            for element in state.textPromptElements:
                                key = element.getKey()
                                promptComponentByKey[key] = gr.Textbox(
                                    label=element.label,
                                    value=presets.getPromptValue(presetName, key),
                                    lines=2,
                                )
                        with gr.Column(scale=3):
                            savePresetButton = gr.Button("Save")
                            savePresetButton.click(
                                fn=self.getOnSavePreset(
                                    presets,
                                    presetName,
                                    list(promptComponentByKey.keys())
                                ),
                                inputs=[presetNameTextbox, *promptComponentByKey.values()],
                            ).then(
                                fn=lambda: [str(uuid.uuid4()), ""],
                                outputs=[refreshPresetsTrigger, newPresetName],
                            )
                            deleteButton = ButtonWithConfirm("Delete", "Confirm delete", "cancel")
                            deleteButton.click(
                                fn=self.getOnDeletePreset(presets, presetName),
                            ).then(
                                fn=lambda: [str(uuid.uuid4()), ""],
                                outputs=[refreshPresetsTrigger, newPresetName],
                            )


            refreshPresetsButton = gr.Button(elem_classes=["refresh-presets", "mcww-hidden"])
            refreshPresetsButton.click(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshPresetsTrigger],
            )

