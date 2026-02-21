## Changelog

### 1.5 - Search update
- Support negatives in loras and presets filter
- Filter is insensitive to words order now
- Added Ctrl+L hotkey to focus on filter
- Improved webui state for batch inputs and outputs
- Improved pseudo gallery UX: now it feels more like a normal gallery with highlighted selected item, and persistent selected item on gallery update
- Documentation of many features
- Added changelog (no changelog file before this version)

### 1.4 - Batch update

- Batch support: "batch" tab in media prompt element is not WIP now
- Batch count parameter: if your workflow has any seed component, this parameter is available, and will automatically increase seeds by 1 for each generation in the batch
- Support for string as output node: use "Preview as Text" as output node, it will be shown in MCWW. It means now you can use workflows like Whisper, QwenVL in the minimalistic
- Added pseudo galleries for text and audio: multiply outputs is supported for audio and text in spite of gradio doesn't support them in galleries. It uses dataset component in pair of audio and textbox components. I call it pseudo because you don't see the content in items' preview, only index
- Presets filter: if there is too many presets, a filter appears
- Page mechanism overhaul: page selection moved to frontend
- Added @synchronized decorators from wrapt library
- New options: hide workflows, mirror camera

### 1.3 - Audio update
- Audio support: now you can use "Load audio"/"Save audio" nodes in MCWW. It means you can now create workflows for music generation (e.g. ace step 1.5), and others

### 1.2 - PWA update

- File name association: on desktop if app installed as PWA, it adds association with image files. RMB -> Open in -> MCWW on any image. Reinstallation required for these changes
- Improved UX and UI in PWA
- Added "Install as PWA", "Free cache and unload models" buttons in management tab
- New option: "Initial video volume in galleries"

### 1.1 - Shallow subgraphs update

- Support for workflows with subgraphs (not nested)
- A lot of fixes of bugs, UI and UX

### 1.0 - Release

- Release! Thanks for early testers before this version. The features on release:
- Queue page with previews, reordering, pause/cancel buttons etc
- Queue saved on disk
- Project page with workflows dynamically rendered (main feature of MCWW), with support of tabs, custom accordions, basic nodes deactivation if no image uploaded; supported image, video, string, numbers
- Can have many projects
- Presets
- Image editor
- WebUI state is saved into browser storage
- Helpers page with tabs: Loras, Management, Metadata, Compare images,  Info, Hotkeys,  Debug
- Options page with options with basic options
- Progress bar
- Smart browser's title
- Basic PWA support
- "Has media" indicator in prompt tabs
