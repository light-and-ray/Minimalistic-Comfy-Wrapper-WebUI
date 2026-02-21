# More about other features

## Loras

To use loras you need to install extension [comfyui-prompt-control](https://github.com/asagi4/comfyui-prompt-control), and use the node `PC: Schedule LoRAs`. It's compatible with all models. Use it instead of the regular `Load LoRa` node. You should either make a title for it like `<Loras:prompt:2>` or connect a new `String (multiline)` node with this title to it. I don't recommend connecting the main prompt to use lora tags directly in it because in this case the lora tag itself will be visible for the model, unless you want to replace clip encoding nodes with prompt control's equivalent, what is less versatile. You definitely need separate lora strings for Wan2.2 hight noise and low noise loras

![](/docs/assets/moreAboutOtherFeatures/promptControl.png)

If you use `Load LoRa` nodes, I recommend you still use these nodes in addition to prompt control nodes, instead of adding them in each prompt for each generation

You don't have to use prompt control specifically, some node mega packs can also include a similar lora loader node. But I personally don't like mega packs

## Debug tab & logs directory

In helpers page there is "Debug" tab. It shows any warnings or errors occurred while parsing workflows. If you don't see a workflow on project page, you can find a reason why it's not shown in debug tab

In `storage/logs` directory you will find all stack traces and dumped workflows sent to comfy in case of any errors, either it's an execution error, or internal MCWW error

## Presets and loras filter

In "loras" tab on helpers page, there is a filter. The same filter appears next to presets in project page, when there are too many presets. Features of this filter:
- case insensitive
- leet insensitive (*"slider for flux"* will find *"sl1d3r4flux"*, *"details"* will find *"d3t4115"*)
- suffix *s* insensitive
- however more precise results appear higher
- word order insensitive
- supports negatives (minus in the word beginning)
- negatives require exact spelling
- in loras, file name matches are higher than directory name matches

## Presets recovery

If the key on text prompt nodes changed (e.g. you moved the title to a different node, changed default value), MCWW will show the old broken values in "edit presets" ui, so you can manually recover them. You can also make auto replacement of old json keys to new keys in any text editor in the presets file in `storage/presets` directory. IMPORTANT! make back ups if you edit files manually. If you accidentally break json syntax (e.g. extra or missing comma or quote) it will destroy the file

Also if you have renamed a workflow, you need to manually rename the workflow presets file in `storage/presets` directory

## Metadata

Metadata tab on helpers page renders workflow if the file was generated in MCWW (the same titles mechanism). If the workflow in metadata can't be rendered (e.g. made in a regular comfy ui workflow), it will show only json in prompt and graph formats (api and non api formats). Also if the file contains PNG Info "parameters", it will show them (used in A1111, Forge, NeoForge), but only for png images

There is no difference in tabs ("Any file", "Image" etc), they are needed to allow OS to select a media picker of correct file type (e.g. on Android image gallery, video gallery etc)

## Compare images

You can use 🡒A, 🡒B, A|B gallery buttons, or hotkeys A, B, C to compare any images in any galleries. Including input and output images inside "Metadata" tab. Or you can use "Compare images" tab on helpers page. You can upload either 2 images A and B, or upload a stitched image. To generate stitched images in workflows use ComfyUI node "Image Stitch"

## Closed sidebar navigation

You still can navigate through pages when the sidebar is closed. To access queue page click on the circle queue indicator next to toggle sidebar button (active even there is no queued tasks). To access helpers page click the small rectangle button next to left bottom corner. To open project page click the button again. On desktop you can also use hotkeys

## Reload button

In the footer there is "Reload" button. It performs autosave of UI state before the reload, so it's safer the normal browser's reload button. Also in PWA app mode on a phone it's the only way to reload the app

## Thumbnails

Thumbnails are generated for videos in queue page if `ffmpeg` is installed in the system. I recommend you to install it, because having image thumbnails instead of videos themselves in queue page significantly optimizes the UI

You can clear thumbnails cache using the button inside "Management" tab. You need to clear the cache if new videos have the same names as the old, e.g. you deleted files from "output" directory in comfy ui installation. Clearing cache using this button will also clear thumbnails from `storage/queue.bin` file, what is not possible by simple deleting `storage/thumbnails` directory

Thumbnails don't work in `direct_links` standalone server mode

## Keys in "Info" tab

In "Info" tab you can see different keys.
- "Gradio browser storage key" and "Gradio browser storage encryption key" - they are used to save webui state (entered values) in browser's storage
- "Queue restore key" - it's used to restore queue from `storage/queue.bin` file on MCWW startup
- "MCWW browser storage key" - used to save some miscellaneous webui state in browser's storage (e.g. resize handle state)

These keys are calculated automatically based on source code files hash. If new MCWW update changes source code of files, responsible for ui state or queue mechanism, it will automatically change the keys, and so delete the incompatible ui state or queue. So you need to be ready for wiping your states or queue after some updates

You can manually trigger reset of webui state by deleting `storage/browser_storage_encryption_key` file, or reset of queue by deleting `storage/queue.bin` file
