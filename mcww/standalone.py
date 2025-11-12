from mcww import opts
from mcww.ui.mainUI import MinimalisticComfyWrapperWebUI

if __name__ == "__main__":
    opts.initializeStandalone()
    MinimalisticComfyWrapperWebUI().launch()
