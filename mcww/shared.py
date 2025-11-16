import gradio as gr
from mcww.ui.mcwwAPI import API

webUI: gr.Blocks = None
api: API = None
presetsUIStateComponent: gr.State = None
runJSFunctionKwargs = None
dummyComponent: gr.Textbox = None

rejectedWorkflows = dict[str, str]()
