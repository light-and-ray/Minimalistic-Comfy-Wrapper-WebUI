import os
import gradio as gr
from mcww import shared
from mcww.utils import saveLogError, insensitiveSearch
from mcww.comfy import comfyAPI

def _getLorasState():
    try:
        loras = comfyAPI.getLoras()
        loras = [lora.removesuffix('.safetensors') for lora in loras]
        return loras
    except Exception as e:
        if type(e) == comfyAPI.ComfyIsNotAvailable:
            gr.Warning("Comfy is not available")
        else:
            saveLogError(e, "Error on get loras state")
            gr.Warning("Unexpected error on get loras state. Check logs for details")
    return []


def _getLorasTable(loras: list[str], originalFilter: str = ""):
    try:
        if loras is None:
            loras = []
        table = ""
        filter = insensitiveSearch(originalFilter)
        toShow = list[str]()
        if filter:
            for lora in loras:
                if filter not in insensitiveSearch(os.path.basename(lora)):
                    continue
                toShow.append(lora)
            for lora in loras:
                if lora in toShow:
                    continue
                directory = lora.removesuffix(os.path.basename(lora))
                if filter not in insensitiveSearch(directory):
                    continue
                toShow.append(lora)
        else:
            toShow = loras

        if filter:
            table += f"Filter **'{originalFilter}'** applied, found: **{len(toShow)}**\n\n"
        table += "|    |\n"
        table += "|----|\n"
        if len(toShow) == 0:
            table += "| Nothing found |\n"
        for lora in toShow:
            table += f"| `<lora:{lora}:1.0>` |\n"
        return table
    except Exception as e:
        saveLogError(e, "Error on get loras table")
        gr.Warning("Unexpected error on get loras table. Check logs for details")
    return None


def buildLorasUI():
    with gr.Column():
        lorasState = gr.State()
        with gr.Row(equal_height=True, elem_classes=["vertically-centred"]):
            gr.Markdown("### Copy loras from here in format for extensions like Prompt Control")
            filter = gr.Textbox(label="Filter:", value="", elem_classes=["mcww-loras-filter"])
        with gr.Row():
            lorasTableComponent = gr.Markdown(elem_classes=["mcww-loras-table", "mcww-table", "no-head"])
            refresh = gr.Button("Refresh", scale=0, elem_classes=["mcww-refresh", "mcww-text-button"])
        gr.on(
            triggers=[filter.change, lorasState.change],
            fn=_getLorasTable,
            inputs=[lorasState, filter],
            outputs=[lorasTableComponent],
        )
        gr.on(
            triggers=[refresh.click, shared.webUI.load],
            fn=_getLorasState,
            outputs=[lorasState],
        )


