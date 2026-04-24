import gradio as gr
from mcww import shared, opts
from mcww.presets import Presets
from mcww.ui.presetsUIUtils import PresetsUIState


def renderPresetsInWorkflowUI(workflowName: str, textPromptElementUiList: list, selectAllButton: gr.Button,
                    presetsBatchDropdown: gr.Dropdown, selectedPresetsBatchMode: gr.Checkbox):
    presets = Presets(workflowName)
    with gr.Column():
        elementKeys = [x.element.getKey() for x in textPromptElementUiList]
        elementComponents = [x.gradioComponent for x in textPromptElementUiList]

        filterVisible = len(presets.getPresetNames()) >= opts.options.presetsFilterThreshold
        filterComponent = gr.Textbox(label="Presets filter", elem_classes=["mcww-tiny-element", "presets-filter"], visible=filterVisible, render=False)
        presetsDataset = gr.Dataset( # gr.Examples apparently doesn't work in gr.render context
            sample_labels=presets.getPresetNames(),
            samples=presets.getPromptsInSamplesFormat(elementKeys),
            components=elementComponents,
            samples_per_page=opts.options.presetsPerPageLimit,
            show_label=False,
            elem_classes=["presets-dataset"],
            render=False,
        )
        savedFiltersDataset = gr.Dataset(show_label=False,
            sample_labels=presets.getSavedFiltersNames(),
            samples=presets.getSavedFiltersInSamplesFormat(),
            samples_per_page=99999,
            components=[filterComponent],
            elem_classes=["force-text-style", "saved-filters-dataset"],
            render=False,
        )
        editPresetsButton = gr.Button("Edit presets", scale=0, elem_classes=["mcww-text-button", "small-button", "edit-presets-button"], render=False)

        with gr.Column():
            presetsDataset.render()
            with gr.Row(elem_classes=["floating-row", "right-aligned"], equal_height=True):
                editPresetsButton.render()
        batchModeVisible = len(presetsDataset.sample_labels) > 1
        with gr.Row(elem_classes=["left-aligned"], visible=batchModeVisible) as filterAndModeRow:
            filterComponent.render()
            if filterVisible:
                selectAllButton.value += " (filtered)"
            selectedPresetsBatchMode.elem_classes.append("mcww-tiny-element")
            selectedPresetsBatchMode.render()
        savedFiltersDataset.render()

        def onPresetSelectedSingle(batchMode: bool, preset: list):
            if batchMode:
                result = [gr.update()] * len(preset)
            else:
                result = preset
            if len(result) != 1:
                return result
            else:
                return result[0]
        presetsDataset.select(
            **shared.runJSFunctionKwargs("scrollToPresetsDataset.storePosition")
        ).then(
            fn=onPresetSelectedSingle,
            inputs=[selectedPresetsBatchMode, presetsDataset],
            outputs=elementComponents,
        ).then(
            **shared.runJSFunctionKwargs("scrollToPresetsDataset.scrollToStoredPosition")
        )

        def onPresetSelectedBatch(batchMode: bool, alreadySelectedPresets: list[str], event: gr.SelectData):
            if not batchMode:
                return gr.update()
            preset = event.value[0]
            result = alreadySelectedPresets
            if preset not in result:
                result.append(preset)
            return gr.Dropdown(value=result)
        presetsDataset.select(
            fn=onPresetSelectedBatch,
            inputs=[selectedPresetsBatchMode, presetsBatchDropdown],
            outputs=[presetsBatchDropdown],
        ).then(
            **shared.runJSFunctionKwargs("scrollPresetsBatchDropdownToBottom")
        )

        savedFiltersDataset.select(
            fn=lambda x: x[0],
            inputs=[savedFiltersDataset],
            outputs=[filterComponent],
        )

        def onSelectAll(filter: str, oldPresets: list[str]):
            result = oldPresets
            for newPreset in presets.getPresetNames(filter=filter):
                if newPreset not in result:
                    result.append(newPreset)
            return gr.Dropdown(value=result)
        selectAllButton.click(
            fn=onSelectAll,
            inputs=[filterComponent, presetsBatchDropdown],
            outputs=[presetsBatchDropdown],
        )

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
            presetsUpdate = gr.Dataset(
                sample_labels=presets.getPresetNames(filter=filter),
                samples=presets.getPromptsInSamplesFormat(elementKeys, filter=filter),
            )
            savedFiltersUpdate = gr.Dataset(
                sample_labels=presets.getSavedFiltersNames(),
                samples=presets.getSavedFiltersInSamplesFormat(),
            )
            if filter:
                filterVisible = True
                batchModeVisible = True
            else:
                filterVisible = len(presetsUpdate.sample_labels) >= opts.options.presetsFilterThreshold
                batchModeVisible = len(presetsUpdate.sample_labels) > 1
            filterUpdate = gr.Textbox(visible=filterVisible)
            filterAndModeRowUpdate = gr.Row(visible=batchModeVisible)
            if not filterVisible:
                savedFiltersUpdate.visible = False
            return presetsUpdate, savedFiltersUpdate, filterUpdate, filterAndModeRowUpdate

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
                outputs=[presetsDataset, savedFiltersDataset, filterComponent, filterAndModeRow],
                show_progress='hidden' if not showProgress else 'minimal',
            ).then(
                **shared.runJSFunctionKwargs("calculatePresetDatasetHeights")
            )
            return dependency
        attachRefreshDatasetListener(afterPresetsEditedButton.click, showProgress=False, needReload=True)
        attachRefreshDatasetListener(filterComponent.change, showProgress=True, needReload=False)
        attachRefreshDatasetListener(refreshPresetsButton.click, showProgress=False, needReload=False)

