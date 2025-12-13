# (Pre-release) Minimalistic Comfy Wrapper WebUI

This is a UI extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) adding an additional inference focused UI, that dynamically adapts to your workflows - you only need to change the titles of nodes that you want to see in the Minimalistic webui, and click "Refresh" button. Also can work as a standalone server

![](docs/assets/readmeMainImage.png)

You have working workflows inside your ComfyUI installation, but you would want to work with them from a different perspective, simpler for inference, with all the noodles hidden? Want to use it on a phone? You find existing solutions like SwarmUI or ViewComfy too overengineered? So this project is made for you

## Key features:
1. Stability: you don't need to be afraid of refreshing/closing the page - everything you do is kept in browser's local storage (like in ComfyUI). It only resets on the project updates to prevent unstable behavior
1. Work in Comfy and in this webui with the same workflows: you don't need to copy anything or to export in api format. Edit your workflows in Comfy - press "Refresh" button, and see the changes in MCWW
1. Better queues: you can change the order of tasks, pause/resume the queue, and don't worry closing Comfy / rebooting your PC during generations
1. Prompt presets: save your favorite prompts in presets next to the input fields, and retrieve them in 1 click

Don't hesitate to report any issues. Leave a star ⭐ on github if you like this project

## Installation

The easiest way to use this webui - install it from ComfyUI manager:
1. WIP

If everything is fine, you should see this button inside ComfyUI:
![](docs/assets/comfyExtensionButton.png)

If you have troubles see [this installation guide](/docs/installation.md)

## Node titles

Full information on node titles is available [here](/docs/titles.md)


## Roadmap to version 2.0
- Audio and Boolean elements support
- Batch processing
- Remake queue and outputs frontend requests using SSE
