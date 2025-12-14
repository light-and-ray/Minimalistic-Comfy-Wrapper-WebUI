> [!NOTE]
> Due to [this ComfyUI_frontend bug](https://github.com/Comfy-Org/ComfyUI_frontend/issues/7185) the node titles are not saved if they are the only changed thing. So if you have problem with saving node titles, you need to make a dummy change, e.g. increment seed, and then press Ctrl+S


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
- if you want to see default value in load image or video nodes inside mcww, you should add `show_default` in other args to it. E.g. `<Reference image:important:1> show_default`
- if your text prompt is in json format, you can set the other args to json, to enable json code editor instead of regular textarea, with syntax highlight and drag-n-drop. E.g. `<Json prompt:prompt:1> json`


Nodes that are tested and should work as UI components are:
- `Clip text encode`
- `Text encode Qwen Image Edit (Plus)`
- `Load Image` / `Save Image`
- `Load Video` / `Save Video`
- Primitives: `Int`, `Float`, `String` (TODO: `Boolean`), or general `Primitive` for the same types
- TODO: model dropdowns

To support other nodes in case they don't work via titles, just connect primitives to them. If you think some nodes should be supported, please don't hesitate to open an issue

To make a seed component (i.e. random is controlled by MCWW + 🎲, ♻️ buttons in UI) the component's label should contain "seed" (in any case), and be integer with no min, max, step args

