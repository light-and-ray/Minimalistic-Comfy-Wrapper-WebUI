import gradio as gr
from mcww.utils import AttrDict

hotkeyTables = AttrDict()

hotkeyTables.t1 = """
### Navigation
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Q**        | Open Queue page or go back                                      |
| **H**        | Open Helpers page or go back                                     |
| **O**        | Open Options page or go back                                       |
| **P**        | Ensure Project page is open                                 |
| **1 - 9**      | Select tab on Helpers and Options pages, or priority on Queue page      |
| **Go Back** | Close the sidebar on mobile                                      |
| **Backquote (~`)** |  Open/close sidebar      |
"""

hotkeyTables.t2 = """
### General
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Alt+V**  | Open clipboard history menu (can also use with Ctrl or Shift)           |
| **Ctrl+V**  | Open a file (image) from the system clipboard   |
| **Shift+RMB** | (Right Mouse Button) Force-open browser's context menu     |
| **Escape** |  Remove focus from the active textbox   |
| **Escape** |  Click a cancel button inside a clicked button with confirmation        |
| **Escape** |  Close all toast notifications    |
| **R**      | Click a visible refresh button                                               |
"""

hotkeyTables.t3 = """
### Cursor over a gallery
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **S**        | Click Download button                |
| **F**        | Toggle fullscreen      |
| **Q**, **Go Back** or **Escape**  | Exit fullscreen                                      |
| **A**, **B**, **C** | Click 🡒A, 🡒B or A\\|B button               |
| **Ctrl+C**   | Click ⎘ button                         |
| **Ctrl+V**   | Click Paste in upload areas under the cursor         |
| **M**        | Toggle markdown in text outputs                |
| **Space**    | Toggle pause in video/audio              |
| **E**        | Open in image editor or return to it                |
| **Ctrl+E** or **Shift+E** | Force-open in image editor, i.e. don't return to already opened image   |
"""

hotkeyTables.t4 = """
### Image editor
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

hotkeyTables.t5 = """
### Compare page/tab
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **+/-**      | Modify opacity                       |
| **S**        | Click Swap button                    |
| **Ctrl+S**   | Click Download composite button                    |
| **C**        | Exit Compare page                                        |

### Project page
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Ctrl+Enter** | Click Run button                        |
| **Ctrl+L** |  Focus on presets filter          |

### Queue page
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Arrows**   | Select previous/next entry in queue                            |
| **Alt/Ctrl+Arrows** | Move selected queue entry up or down                      |

### Other pages/tabs
| Key          | Action                                                            |
|--------------|-------------------------------------------------------------------|
| **Ctrl+S**   | Click Save or Add button on Presets page                                |
| **Ctrl+Shift+S**  | Click Save as copy or Add button on Presets page                                |
| **Ctrl+L**   | Focus on loras filter on Loras tab  |
| **Escape**   | Exit File Open page    |
| **A**        | Toggle auto refresh checkbox on Management tab                 |
| **Ctrl+V**   | Paste file from clipboard on Metadata tab             |
"""


def buildHotkeysUI():
    with gr.Row(elem_classes=["horizontally-centred", "allow-pwa-select"]):
        tables = sorted(hotkeyTables.values(), key=lambda x: len(x.split('\n')))
        for table in tables:
            with gr.Column():
                gr.Markdown(table, elem_classes=["mcww-table", "no-head", "hotkeys-table"])

