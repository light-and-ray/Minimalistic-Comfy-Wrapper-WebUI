import gradio as gr
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcww.ui.mcwwAPI import API
    from mcww.comfy.messages import Messages


messages: "Messages" = None
webUI: gr.Blocks = None
localUrl: str = None
api: "API" = None
presetsUIStateComponent: gr.State = None
dummyComponent: gr.Textbox = None
dummyComponentBool: gr.Checkbox = None


def runJSFunctionKwargs(jsFunctions) -> dict:
    if isinstance(jsFunctions, str):
        jsFunctions = [jsFunctions]
    jsCode = '(async function (...args) {'
    for jsFunction in jsFunctions:
        jsCode += f"await {jsFunction}();"
    jsCode += '})'
    return dict(
            fn=lambda x: x,
            inputs=[dummyComponent],
            outputs=[dummyComponent],
            js=jsCode,
    )


class WarningsContext:
    def __init__(self):
        self.warnings = {}
        self.context_stack = []

    def __call__(self, context_name):
        """Return self to allow chaining with 'with' statement"""
        self._entering_context = context_name
        return self

    def __enter__(self):
        context_name = self._entering_context
        self.context_stack.append(context_name)
        if context_name not in self.warnings:
            self.warnings[context_name] = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        current_context = self.context_stack[-1]
        if not self.warnings[current_context]:
            del self.warnings[current_context]
        self.context_stack.pop()
        return False

    def warning(self, message):
        """Add a warning to the current context"""
        if self.context_stack:
            current_context = self.context_stack[-1]
            self.warnings[current_context].append(message)
        else:
            print("No active warnings context")
            print(message)

    def getDict(self):
        """Get a copy of all warnings"""
        return self.warnings.copy()

    def clear(self):
        """Clear all warnings"""
        self.warnings = {}


workflowsLoadingContext = WarningsContext()
commandLineArgs: list[str]|None = None
clientID: str = None
