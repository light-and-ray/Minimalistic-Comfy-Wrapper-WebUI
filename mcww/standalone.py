import os
from mcww import opts
from mcww.ui.mainUI import MinimalisticComfyWrapperWebUI

if __name__ == "__main__":
    opts.initializeStandalone()
    os.makedirs(opts.STORAGE_DIRECTORY, exist_ok=True)
    MinimalisticComfyWrapperWebUI().launch()
