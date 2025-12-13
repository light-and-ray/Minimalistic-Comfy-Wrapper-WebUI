import gradio as gr

hotkeysReferenceMd = """
## Hotkeys Reference
### General

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **R**        | Click Refresh button                                               |
| **Q**        | Open/Close Queue page                                              |
| **H**        | Open/Close Helpers page                                                 |
| **O**        | Open/Close Options page                                                 |
| **P**        | Ensure Project page is open                                 |
| **1 - 9**      | Select tab on Helpers page                             |
| **Ctrl+Enter** | Click Run Button                                                 |
| **Go Back** | Close the sidebar on mobile                                      |
| **Escape** |  Remove focus from active textbox   |
| **Escape** |  Click cancel inside clicked button with confirmation        |
| **Escape** |  Close toast notifications    |

### Cursor over a gallery
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **S**        | Click Download button                |
| **F**        | Toggle Fullscreen button      |
| **A**        | Click 🡒A button               |
| **B**        | Click 🡒B button           |
| **C**        | Click A\\|B button               |
| **Space**    | Toggle pause in video               |
| **Ctrl+C**   | Click ⎘ button                         |
| **Ctrl+V**   | Click Paste in image upload area under the cursor         |
| **Go Back**  | Exit fullscreen                                      |
| **Escape**  | Exit fullscreen                                      |
| **E**        | Open in image editor or return to it                |
| **Ctrl+E** or **Shift+E** | Forcefully open in image editor, i.e. don't return to already opened image   |

### Image/Mask editor
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **1 - 9**    | Select tool                             |
| **[/]**  | Change brush size                           |
| **+/-**  | Change opacity                           |
| **C**        | Choose color               |
| **Ctrl+Z**   | Undo                     |
| **Ctrl+Y** or **Ctrl+Shift+Z**   | Redo                     |
| **Ctrl+S**   | Save and go back                               |
| **Go Back**  | Cancel and go back                                    |
| **Go Forward**  | Return to the editor                                   |

### Other pages
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Arrows**   | Select previous/next entry in queue                            |
| **Alt+Arrows** | Move selected queue entry up or down                      |
| **+/-**      | Modify opacity on Compare page/tab                            |
| **S**        | Click Swap button on Compare page/tab                            |
| **Ctrl+S**   | Click Download composite button on Compare page/tab                    |
| **Ctrl+S**   | Click Save button on Presets page                                |
| **A**        | Toggle auto refresh checkbox on Management page                 |
"""


def buildHotkeysUI():
    gr.Markdown(hotkeysReferenceMd, elem_classes=["mcww-table", "no-head"])

