import gradio.processing_utils

old_save_pil_to_cache = gradio.processing_utils.save_pil_to_cache
def new_save_pil_to_cache(*args, **kwargs):
    if not kwargs.get("name") and getattr(args[0], '_mcww_filename', None):
        filename: str = args[0]._mcww_filename
        format: str = kwargs.get("format", "png").lower()
        filename = filename.removesuffix(f".{format}")
        kwargs["name"] = filename
    return old_save_pil_to_cache(*args, **kwargs)

gradio.processing_utils.save_pil_to_cache = new_save_pil_to_cache
