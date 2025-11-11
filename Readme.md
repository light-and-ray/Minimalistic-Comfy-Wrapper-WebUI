# (Beta) Minimalistic Comfy Wrapper WebUI

An alternative additional non-node based UI for [ComfyUI](https://github.com/comfyanonymous/ComfyUI), that dynamically adapts to your workflows - you only need to change the titles of nodes that you want to see in the Minimalistic webui, and click "Refresh" button

![](docs/assets/readmeMainImage.png)

You have working workflows inside your ComfyUI installation, but you would want to work with them from a different perspective, simpler for inference, with all the noodles hidden? Want to use it on a phone? You find existing solutions like SwarmUI or ViewComfy too overengineered? So this project is made for you

## Key features:
1. Stability: you don't need to be afraid of refreshing/closing the page - everything you do is kept in browser's local storage (like in ComfyUI). It only resets on the project updates to prevent unstable behavior
1. Work in Comfy and in this webui with the same workflows: you don't need to copy anything or to export in api format. Edit your workflows in Comfy - press "Refresh" button, and see the changes in MCWW
1. Better queues: you can change the order of tasks, pause/resume the queue, and don't worry closing Comfy / rebooting your PC during generations (Coming soon)
1. Prompt presets: save your favorite prompts in presets next to the input fields, and retrieve them in 1 click

Don't hesitate to report any issues

## Installation

The easiest way to use this webui - install it as ComfyUI extension. To do it:
1. Clone this repository into `custom_nodes/` directory inside your ComfyUI installation: `git clone https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI`
1. Activate ComfyUI python environment in command line for the next step. If you don't know what is it, so probably you didn't install ComfyUI using it. Try to use `python_embeded\python -m pip` from the portable installation instead of `pip` command in the next step. If you have troubles with the installation, don't hesitate to open an issue
1. Install requirements from this extension root `pip install -r requirements.txt`
1. If you use ComfyUI-Login extension or HTTPS connection, you also need to setup `COMFY_UI_LOGIN_EXTENSION_TOKEN` or `COMFY_TLS` environment variables inside `.env` file in the root of extension (or outside, if you will). In this case you may also want to set a password on MCWW too, use `MCWW_AUTH` variable fot it
1. You also should have `ffmpeg` in `PATH`. It's not mandatory, but otherwise you can experience lags (especially on a smartphone) in queue page if there are a lot of videos

If everything is fine, you should see this button inside ComfyUI:
![](docs/assets/comfyExtensionButton.png)

Alternately you can run this webui as a standalone server:
1. Clone this repo somewhere you like
1. Use `.env.example` to create your own `.env` file
1. Create python virtual environment `python -m venv venv`
1. Activate this environment `. venv/bin/activate` in Linux or `call venv\Scripts\activate.bat` in Windows
1. Install requirements `pip install -r requirements.txt`
1. Use `./standalone-start.py` or `python standalone-start.py` (on Windows) to start the server (even if venv is not activated)

## Node titles

In order to a node to appear as an element inside MCWW, it has to have a special title in this simple format: `<Label:category[/tab]:sortRowNumber[/sortColNumber]> other args`. Categories are: "prompt", "output", "important", "advanced" (or their plural forms), or a custom category. "prompt" and "output" are mandatory. Some other components accept additional properties after the title, for example min, max, step (for CFG in examples) is used to set a range and steps for Slider component. Examples:
- `<Prompt:prompt:1>`
- `<Image 1:prompt/Image 1:1>`
- `<Image 2:prompt/Image 2:2>`
- `<Image 3:prompt/Image 3:3>`
- `<Output:output:1>`
- `<Stitched:output:2>`
- `<CFG:advanced:2/2> 1, 10, 0.1` - will appear inside "advanced" accordion under text prompts (row 2 col 2)
- or `<CFG:advanced/General:1> 1, 10, 0.1` - will appear inside "advanced" accordion inside "General" tab. You can set any tab name here. Sort number is needed to sort components inside each category and tab. Tabs themselves are sorted by the lowest sort number among elements inside them
- or `<CFG:important:1> 1, 10, 0.1` - will be shown under outputs
- You can make a custom category. In this case they will be added at the end of page inside their own accordions (ala A1111 extensions): `<Enabled:ControlNet:1>`
- You can use any node as prompt, not only text/media. For example StyleGan (this person does not exist) accepts only seed as input, but "prompt" category is mandatory. So do this: `<Seed:prompt:1>`


Nodes that are tested and should work as UI components are:
- `Clip text encode`
- `Text encode Qwen Image Edit (Plus)`
- `Load Image` / `Save Image`
- `Load Video` / `Save Video`
- Primitives: `Int`, `Float`, `String` (TODO: `Boolean`), or general `Primitive` for the same types
- TODO: model loaders

To support other nodes in case they don't work via titles, just connect primitives to them. If you think some nodes should be supported, please don't hesitate to open an issue

To make a seed component (i.e. random is controlled by MCWW + 🎲, ♻️ buttons in UI) the component's label should contain "seed" (in any case), and be integer with no min, max, step args


## Roadmap to the Release version
- ☑️ Video support
- ☑️ Add prompt presets
- Keep queue on a disk
- Add webui settings
- Add progress bar
