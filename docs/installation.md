
Installation via ComfyUI manager is described in the [readme](https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI?tab=readme-ov-file#installation)

Install manually as an extension:
1. Clone this repository into `custom_nodes/` directory inside your ComfyUI installation: `git clone https://github.com/light-and-ray/Minimalistic-Comfy-Wrapper-WebUI`
1. Activate ComfyUI python environment in command line for the next step. If you don't know what is it, so probably you didn't install ComfyUI using it. Try to use `python_embeded\python -m pip` from the portable installation instead of `pip` command in the next step. If you have troubles with the installation, don't hesitate to open an issue
1. Install requirements from this extension root `pip install -r requirements.txt`
1. If you use ComfyUI-Login extension or HTTPS connection, you also need to setup `COMFY_UI_LOGIN_EXTENSION_TOKEN` or `COMFY_TLS` environment variables inside `.env` file in the root of extension (or outside, if you will). In this case you may also want to set a password on MCWW too, use `MCWW_AUTH` variable fot it
1. You also should have `ffmpeg` in `PATH`. It's not mandatory, but otherwise you can experience lags (especially on a smartphone) in queue page if there are a lot of videos


Alternately you can run this webui as a standalone server:
1. Clone this repo somewhere you like
1. Use `.env.example` to create your own `.env` file
1. Create python virtual environment `python -m venv venv`
1. Activate this environment `. venv/bin/activate` in Linux or `call venv\Scripts\activate.bat` in Windows
1. Install requirements `pip install -r requirements.txt`
1. Use `./standalone-start.py` or `python standalone-start.py` (on Windows) to start the server (even if venv is not activated)
