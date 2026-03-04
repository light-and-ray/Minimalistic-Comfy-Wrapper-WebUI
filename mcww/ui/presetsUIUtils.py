import gradio as gr
import json
from dataclasses import dataclass
from mcww.presets import Presets
from mcww.comfy.workflow import Element

@dataclass
class PresetsUIState:
    textPromptElements: list[Element]
    workflowName: str
    selectedPreset: str = None


class PresetsUiActions:
    @staticmethod
    def getOnAddPreset(presets: Presets, promptComponentKeys: list[str]):
        def onAddPreset(newPresetName: str, *prompts):
            if not newPresetName:
                raise gr.Error("New preset name is empty", duration=1, print_exception=False)
            if newPresetName in ["+", "+⌕"]:
                raise gr.Error("New preset name can't be + or +⌕", duration=1, print_exception=False)
            if Presets.SAVED_FILTER_ELEMENT_KEY in promptComponentKeys:
                newPresetName = "⌕ " + newPresetName
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
            if newPresetName in ["+", "+⌕"]:
                raise gr.Error("New preset name can't be + or +⌕", duration=1, print_exception=False)
            if Presets.SAVED_FILTER_ELEMENT_KEY in promptComponentKeys:
                newPresetName = "⌕ " + newPresetName
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
            if newPresetName in ["+", "+⌕"]:
                raise gr.Error("New preset name can't be + or +⌕", duration=1, print_exception=False)
            if Presets.SAVED_FILTER_ELEMENT_KEY in promptComponentKeys:
                newPresetName = "⌕ " + newPresetName
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
        if "+⌕" in newOrder:
            newOrder.remove("+⌕")
        presets = Presets(state.workflowName)
        presets.applyNewOrder(newOrder)
        presets.save()

