# Minimalistic Comfy Wrapper WebUI v1.x

This is a UI extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) adding an additional inference focused UI, that dynamically adapts to your workflows - you only need to change the titles of nodes that you want to see in the Minimalistic webui, and click "Refresh" button. Also can work as a standalone server

![](/docs/assets/readmeMainImage.png)
*More screenshots [here](/docs/moreScreenshots.md)*

You have working workflows inside your ComfyUI installation, but you would want to work with them from a different perspective, simpler for inference, with all the noodles hidden? Want to use it on a phone? You find existing solutions like SwarmUI or ViewComfy too overengineered? So this project is made for you

## Key features:
1. Stability: you don't need to be afraid of refreshing/closing the page - everything you do is kept in browser's local storage (like in ComfyUI). It only resets on the project updates to prevent unstable behavior
1. Work in Comfy and in this webui with the same workflows: you don't need to copy anything or to export in api format. Edit your workflows in Comfy - press "Refresh" button, and see the changes in MCWW
1. Better queues: you can change the order of tasks, pause/resume the queue, and don't worry closing Comfy / rebooting your PC during generations
1. Prompt presets: save your favorite prompts in presets next to the input fields, and retrieve them in 1 click
1. Built-in minimalist image editor, that allows you to add visual prompts to image editing model, or crop/rotate the image
1. Mobile friendly UI. You can use it in browser or as PWA app over local network. Read [this](/docs/pwaAndSecureContext.md) for details

Don't hesitate to report any issues. Leave a star ⭐ on GitHub if you like this project

## Installation
> [!NOTE]
> It looks like the manager db is not fully updated yet and sometimes it can not show available versions, so in this case you need to use [the other installation methods](/docs/installation.md)

The easiest way to use this webui - install it from ComfyUI manager:
1. You should have [ComfyUI Manager](https://github.com/Comfy-Org/ComfyUI-Manager)
1. Open "Manager" -> "Custom Nodes Manager"
1. Search "Minimalistic Comfy Wrapper WebUI" by author light-and-ray
1. Click "Install" and select the latest version. Don't select "nightly" version if you have normal security level, because in this case you will get an error
1. If you use comfy in a cloud or login extension, do [this](/docs/installation.md#specific-environment)
1. Restart ComfyUI after installation

If everything is fine, you should see this button inside ComfyUI:
![](docs/assets/comfyExtensionButton.png)

If you have troubles see [this full installation guide](/docs/installation.md)

## Node titles

You need to mark your input and output nodes with title in special format

For output nodes (SaveImage/SaveVideo) you need to set `<Result:output:1>` as title, where "Result" is a label displayed in ui, "output" is category and 1 is sort number (if you want to have a specific order for multiply elements). This category is mandatory

For main inputs you need to use category "prompt", for example `<Positive prompt:prompt:1>` for text prompt or `<Image 1:prompt:1>` for image prompt. This category is mandatory

Other settings you can bypass using "important", "advanced" or a custom category. Usually for settings you need to use `Primitive` node and connect it to desired widget input. For seed you should create `Int` node with title `<Seed:advanced:1>`

The UI also supports tabs, custom accordions, columns and other things. Full information on node titles is available [here](/docs/titles.md)

## Documentation
- [Full installation guide](/docs/installation.md)
- [.env file example with all possible variables](/.env.example)
- [Full node titles info](/docs/titles.md)
- [Install as an app (PWA) and secure context guide](/docs/pwaAndSecureContext.md)


## Roadmap to version 2.0
- Audio and Boolean elements support
- Batch processing
- Remake queue and outputs frontend requests using SSE
- Masks support
- Lora name validation
- Recursive None nodes auto deactivation
