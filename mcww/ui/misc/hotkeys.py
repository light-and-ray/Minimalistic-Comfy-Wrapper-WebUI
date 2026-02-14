import gradio as gr
from mcww.utils import AttrDict

hotkeyTables = AttrDict()

hotkeyTables.t1 = """
### Navigation

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Q**        | Open/Close Queue page                                              |
| **H**        | Open/Close Helpers page                                                 |
| **O**        | Open/Close Options page                                                 |
| **P**        | Ensure Project page is open                                 |
| **1 - 9**      | Select tab on Helpers page                             |
| **Go Back** | Close the sidebar on mobile                                      |
| **Backquote (~`)** |  Open/close sidebar      |
"""

hotkeyTables.t2 = """
### General

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **R**        | Click Refresh button                                               |
| **Ctrl+Enter** | Click Run Button                                                 |
| **Escape** |  Remove focus from active textbox   |
| **Escape** |  Click cancel inside clicked button with confirmation        |
| **Escape** |  Close toast notifications    |
| **Shift+RMB** |  (Right Mouse Button) Force-open browser context menu in PWA mode    |
"""

hotkeyTables.t3 = """
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
"""

hotkeyTables.t4 = """
### Other pages

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Arrows**   | Select previous/next entry in queue                            |
| **Alt/Ctrl+Arrows** | Move selected queue entry up or down                      |
| **+/-**      | Modify opacity on Compare page/tab                            |
| **S**        | Click Swap button on Compare page/tab                            |
| **Ctrl+S**   | Click Download composite button on Compare page/tab                    |
| **Ctrl+S**   | Click Save button on Presets page                                |
| **A**        | Toggle auto refresh checkbox on Management page                 |
"""

hotkeyTables.t5 = """
### Cursor over a gallery

| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **S**        | Click Download button                |
| **F**        | Toggle Fullscreen button      |
| **A**        | Click 🡒A button               |
| **B**        | Click 🡒B button           |
| **C**        | Click A\\|B button               |
| **Space**    | Toggle pause in video/audio              |
| **Ctrl+C**   | Click ⎘ button                         |
| **Ctrl+V**   | Click Paste in image upload area under the cursor         |
| **Go Back**  | Exit fullscreen                                      |
| **Escape**  | Exit fullscreen                                      |
| **E**        | Open in image editor or return to it                |
| **Ctrl+E** or **Shift+E** | Force-open in image editor, i.e. don't return to already opened image   |
"""


def buildHotkeysUI():
    with gr.Row(elem_classes=["horizontally-centred"]):
        for table in hotkeyTables.values():
            with gr.Column():
                gr.Markdown(table, elem_classes=["mcww-table", "no-head", "hotkeys-table", "allow-pwa-select"])

