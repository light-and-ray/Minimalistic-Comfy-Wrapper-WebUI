import gradio as gr
import threading, time
from mcww.comfy.comfyAPI import getStats, ComfyIsNotAvailable
from mcww.utils import saveLogError
import pandas as pd


class _ComfyStats:
    MAX_HISTORY_SECONDS = 600
    HISTORY_UPDATE_RATE = 1

    def __init__(self):
        self.history = list[dict]()
        self.updaterThread = threading.Thread(target=self._updaterFunction, daemon=True)
        self.updaterThread.start()


    def _updaterFunction(self):
        while True:
            time.sleep(self.HISTORY_UPDATE_RATE)
            try:
                stats = getStats()
            except Exception as e:
                if not isinstance(e, ComfyIsNotAvailable):
                    saveLogError(e, 'error in _ComfyStats._updaterFunction')
            else:
                self.history.append(stats)
                maxSize = self.MAX_HISTORY_SECONDS / self.HISTORY_UPDATE_RATE
                if len(self.history) > maxSize:
                    self.history = self.history[-maxSize:]


    def getVramPlotUpdate(self):
        try:
            totalVram = self.history[0]['devices'][0]['vram_total']
            vramHistory = [totalVram - x['devices'][0]['vram_free'] for x in self.history]
            totalVramGiB = totalVram / (1024 ** 3)
            vramHistoryGiB = [v / (1024 ** 3) for v in vramHistory]
            value = pd.DataFrame({
                'x': range(len(vramHistoryGiB)),
                'vram_used': vramHistoryGiB,
            })
            return gr.LinePlot(value, y_lim=[0, totalVramGiB], x_lim=[0, len(vramHistoryGiB)-1])
        except Exception as e:
            return None


    def getRamPlotUpdate(self):
        try:
            totalRam = self.history[0]['system']['ram_total']
            ramHistory = [totalRam - x['system']['ram_free'] for x in self.history]
            totalRamGiB = totalRam / (1024 ** 3)
            ramHistoryGiB = [v / (1024 ** 3) for v in ramHistory]
            value = pd.DataFrame({
                'x': range(len(ramHistoryGiB)),
                'ram_used': ramHistoryGiB,
            })
            return gr.LinePlot(value, y_lim=[0, totalRamGiB], x_lim=[0, len(ramHistoryGiB)-1])
        except Exception as e:
            return None


comfyStats = _ComfyStats()


def buildInfoTab():
    gr.Markdown("Comfy server stats:")
    with gr.Row():
        vramPlot = gr.LinePlot(
            pd.DataFrame({'x': [], 'vram_used': []}),
            x='x',
            y='vram_used',
            x_axis_labels_visible=False,
            x_title=' ',
            y_title='VRAM Used (GiB)',
        )
        ramPlot = gr.LinePlot(
            pd.DataFrame({'x': [], 'ram_used': []}),
            x='x',
            y='ram_used',
            x_axis_labels_visible=False,
            x_title=' ',
            y_title='RAM Used (GiB)',
        )
    updateButton = gr.Button("Update", elem_classes=["mcww-hidden", "mcww-update-helpers-info-button"])
    @gr.on(
        triggers=[updateButton.click],
        outputs=[vramPlot, ramPlot],
        show_progress='hidden',
    )
    def onInfoTabUpdate():
        return comfyStats.getVramPlotUpdate(), comfyStats.getRamPlotUpdate()


