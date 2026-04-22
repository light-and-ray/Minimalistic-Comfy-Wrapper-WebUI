## Changelog

### (WIP) 2.1
- Markdown view in text output component. Other text argument `md` or `markdown` is supported
- Support for "MarkdownNote" and "Note" nodes
- New option "Restart Comfy if less then specified number of GiB of RAM is available" - to avoid memory shortage OS consequences when using leaking ComfyUI version or leaking custom nodes
- New options: "noteLengthCollapseLimit", "titleInMediaSession"
- Fixed audio IsADirectoryError; progressbar overflow
- Added overflow galleries: now if there are too many entries in galleries, they will be split. The size of this split is 50 by default, can change in a option "Limit outputs in result galleries". This fixes issue when UI hangs due to too many videos or images

## 2.0 Release
- 1.0-2.0 updates brought advanced batch support; pwa, themes, context menu, clipboard improvements; compatibility with comfy ui subgraphs

### 1.8 – Batch quality of life update
- Load and save state of selected tab, opened accordions and presets batch mode for each workflow
- Workaround gradio bug when "Batch" is not rendered
- Added Clipboard history menu: on Alt+V hotkey or in context menu you can open clipboard history and select previously copied files. New option for this "Clipboard history length". Set it to 0 to hide the context menu item. If you have conflict with a system's Alt+V hotkey - you can use Ctrl+Alt+V or Shift+Alt+V
- New option: "Preferred theme Dark/Light"
- Open context menu on 2 fingers tap

### 1.7 – Presets batch & nested subgraphs update
- Presets batch mode: if you have more than 1 preset, you can switch text prompt category into "Presets batch mode". In this mode when you select preset, in goes into "Selected presets" area. After clicking "Run" button it will execute workflow for each set of prompts in each preset. Compatible with batch media inputs, and batch count. You can also use in pair with filter
- Saved preset filters: in presets editor you can save filters. They appear under presets
- New option: "Presets filter appear threshold" (was 30 constant before)
- Support for nested subgraphs! Used in official Flux.2 Klein workflows for example
- Support for `COMFY_DYNAMICCOMBO_V3` node inputs. Used in new "TextGenerate" official node
- Added paste button to batch upload galleries; added "Pasting..." mouse alerts
- Added "open in new window" button in galleries
- Copy and Paste now work for video and audio
- PWA file open also works for video and audio. You need to clear browser's cache and reinstall PWA add to update file associations
- Added custom context menu, with all gallery buttons in it. Useful on phone where gallery buttons are too small

### 1.6 – Priority queue & UI themes update
- Added priorities in queue: added parameter "Priority" into Workflow UI. Queue runner select workflows with higher priority first. In queue page priorities are shown as separate queue. You can change maximal value of priority in the options (set 1 to hide priorities and return the old queue)
- Added hotkey 1-9 buttons to select priority in queue page
- Support for wildcards (`*`, `?`, `[seq]`, `[!seq]`) in hide workflows option
- Added options to change primary color saturation and lightness
- Added option to change theme class and neutral/secondary color
- Added tabs in Options page
- Make the default's background palette for black theme much darker

### 1.5 – Search update
- Support negatives in loras and presets filter
- Filter is insensitive to words order now
- Added Ctrl+L hotkey to focus on filter
- Improved webui state for batch inputs and outputs
- Improved pseudo gallery UX: now it feels more like a normal gallery with highlighted selected item, and persistent selected item on gallery update
- Documentation of many features
- Added changelog (no changelog file before this version)

### 1.4 – Batch update

- Batch support: "batch" tab in media prompt element is not WIP now
- Batch count parameter: if your workflow has any seed component, this parameter is available, and will automatically increase seeds by 1 for each generation in the batch
- Support for string as output node: use "Preview as Text" as output node, it will be shown in MCWW. It means now you can use workflows like Whisper, QwenVL in the minimalistic
- Added pseudo galleries for text and audio: multiply outputs is supported for audio and text in spite of gradio doesn't support them in galleries. It uses dataset component in pair of audio and textbox components. I call it pseudo because it's made of multiply gradio components instead of 1, however in Gradio's CSS, datasets themselves are considered being full-fledged galleries
- Presets filter: if there is too many presets, a filter appears
- Page mechanism overhaul: page selection moved to frontend
- Added @synchronized decorators from wrapt library
- New options: hide workflows, mirror camera

### 1.3 – Audio update
- Audio support: now you can use "Load audio"/"Save audio" nodes in MCWW. It means you can now create workflows for music generation (e.g. ace step 1.5), and others

### 1.2 – PWA update

- File name association: on desktop if app installed as PWA, it adds association with image files. RMB -> Open in -> MCWW on any image. Reinstallation required for these changes
- Improved UX and UI in PWA
- Added "Install as PWA", "Free cache and unload models" buttons in management tab
- New option: "Initial video volume in galleries"

### 1.1 – Shallow subgraphs update

- Support for workflows with subgraphs (not nested)
- A lot of fixes of bugs, UI and UX

## 1.0 Release

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
