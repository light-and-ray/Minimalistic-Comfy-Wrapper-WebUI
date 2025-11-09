import gradio as gr
import uuid
from dataclasses import dataclass
from mcww import shared
from mcww.presets import Presets
from mcww.comfy.workflow import Element


@dataclass
class PresetsUIState:
    textPromptElements: list[Element]
    workflowName: str


class PresetsUI:
    def __init__(self):
        self._buildPresetsUI()


    def _buildPresetsUI(self):
        refreshPresetsTrigger = gr.Textbox(visible=False)

        with gr.Column(visible=False) as self.ui:
            backButton = gr.Button("🡠", elem_classes=["mcww-tool"])
            backButton.click(
                **shared.runJSFunctionKwargs("goBack")
            )
            @gr.render(
                triggers=[refreshPresetsTrigger.change],
                inputs=[shared.presetsUIStateComponent],
            )
            def renderPresets(state: PresetsUIState|None):
                if not state:
                    gr.Markdown("presetsUIState is None", elem_classes=["mcww-visible"])
                    return
                presets = Presets(state.workflowName)
                for presetName in presets.getPresetNames():
                    gr.Markdown(f'## {presetName}:')
                    inputByKey = dict[str, gr.Textbox]()
                    for element in state.textPromptElements:
                        key = element.getKey()
                        inputByKey[key] = gr.Textbox(label=key, value=presets.getPromptValue(presetName, key))

            refreshPresetsButton = gr.Button("Refresh presets", elem_classes=["refresh-presets"])
            refreshPresetsButton.click(
                fn=lambda: str(uuid.uuid4()),
                outputs=[refreshPresetsTrigger],
            )

