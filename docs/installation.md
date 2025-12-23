
## Installation from ComfyUI Registry

- You can use ComfyUI Manager find `"Minimalistic Comfy Wrapper WebUI"` by author light-and-ray there and install it
- Or you can use comfy-cli and install this extension using command `comfy node install mcww-webui`
- To get comfy-cli (`comfy` command) use `pip install comfy-cli`
### I got an error "This action is not allowed with this security level configuration"
- To solve this error try to select the latest version, not "nightly". If it doesn't help - change `security_level = normal` to `security_level = weak` inside `user/__manager/config.ini` file or try other installation methods

## Install manually as an extension:
1. Clone this repository into `custom_nodes/` directory inside your ComfyUI installation: `git clone https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI`
1. Activate ComfyUI python environment in command line for the next step. If you don't know what is it, so probably you didn't install ComfyUI using it. Try to use `python_embeded\python -m pip` from the portable installation instead of `pip` command in the next step. If you have troubles with the installation, don't hesitate to open an issue
1. Install requirements from this extension root `pip install -r requirements.txt`
1. You also should have `ffmpeg` in `PATH`. It's not mandatory, but otherwise you can experience lags (especially on a smartphone) in queue page if there are a lot of videos


## Specific environment
- If you use ComfyUI in a cloud, the UI wont be available because it runs on a port that is not available from the Internet. In this case you need to consider using `GRADIO_SHARE="True"` variable inside .env file (need to create in extension root) to use a tunnel by gradio.live; or you can install MCWW locally on your computer and set it up to use your Comfy from the cloud
- If you use ComfyUI-Login extension, you need to set `COMFY_UI_LOGIN_EXTENSION_TOKEN` variable inside .env file (need to create in extension root). In this case you may also want to set a password on MCWW too, use `MCWW_AUTH` variable for it
- If HTTPS connection, you need to set `COMFY_TLS` variable inside .env file (need to create in extension root)


## Alternately you can run this webui as a standalone server:
1. Clone this repo somewhere you like
1. Use `.env.example` to create your own `.env` file
1. Create python virtual environment `python -m venv venv`
1. Activate this environment `. venv/bin/activate` in Linux or `call venv\Scripts\activate.bat` in Windows
1. Install requirements `pip install -r requirements.txt`
1. Use `./standalone-start.py` or `python standalone-start.py` (on Windows) to start the server (even if venv is not activated)
