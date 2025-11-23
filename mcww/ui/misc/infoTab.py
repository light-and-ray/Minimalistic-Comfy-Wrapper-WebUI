import gradio as gr
import threading, time, subprocess, re
from mcww import opts, shared
from mcww.comfy.comfyAPI import getStats, ComfyIsNotAvailable
from mcww.utils import saveLogError, getJsStorageKey, getStorageEncryptionKey, getStorageKey, getQueueRestoreKey
import pandas as pd


def get_head_commit_info():
    try:
        result = subprocess.run(
            ["git", "show", "HEAD"],
            cwd=opts.MCWW_DIRECTORY,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        commit_match = re.search(r'^commit (\w+)', output, re.MULTILINE)
        commit_hash = commit_match.group(1) if commit_match else None

        date_match = re.search(r'^Date:\s+(.+)', output, re.MULTILINE)
        commit_date = None

        if date_match:
            full_date_string = date_match.group(1).strip()
            # The git date format is typically: 'Day Mon DD HH:MM:SS YYYY Timezone'
            # Example: 'Sun Nov 23 20:31:07 2025 +0400'

            # Use a more specific regex to capture the required parts: YYYY, Mon, DD
            # (\w{3}): Day (e.g., Sun)
            # (\w{3}): Month abbreviation (e.g., Nov) -> Group 1
            # (\d{2}): Day of the month (e.g., 23) -> Group 2
            # (.*?): Time (ignored)
            # (\d{4}): Year (e.g., 2025) -> Group 3
            date_parts_match = re.search(r'^\w{3}\s+(\w{3})\s+(\d{2}).*?(\d{4})', full_date_string)

            if date_parts_match:
                month_abbr = date_parts_match.group(1)
                day = date_parts_match.group(2)
                year = date_parts_match.group(3)
                commit_date = f"{year} {month_abbr} {day}"

        return commit_hash, commit_date

    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None


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
                maxSize = self.MAX_HISTORY_SECONDS // self.HISTORY_UPDATE_RATE
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


    def getSystemInfoMarkdown(self):
        try:
            comfyVersion: str = self.history[0]['system']['comfyui_version']
            comfyArgs: str = self.history[0]['system']['argv']
            gpuName: str = self.history[0]['devices'][0]['name']
            gpuName = gpuName.removeprefix('cuda:0').removesuffix(': cudaMallocAsync').strip()
            return (
                f'- Comfy version: `{comfyVersion}`\n'
                f'- Comfy GPU name: `{gpuName}`\n'
                f'- Comfy command line flags: `{comfyArgs[1:]}`\n'
            )
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
    gr.Markdown(comfyStats.getSystemInfoMarkdown)
    commit, date = get_head_commit_info()
    keysInfo = gr.Markdown(
        f'- WebUI version commit: `{commit}`\n'
        f'- WebUI version date: `{date}`\n'
        f'- Server mode: `{opts.FILE_CONFIG.mode.name.lower()}`, Is standalone: `{opts.IS_STANDALONE}`\n'
        f'- Command line flags: `{shared.commandLineArgs}`\n'
        f'- Gradio browser storage key: `{getStorageKey()}`\n'
        f'- Gradio browser storage encryption key: `{getStorageEncryptionKey()}`\n'
        f'- Queue restore key: `{getQueueRestoreKey()}`\n'
        f'- MCWW browser storage key: `{getJsStorageKey()}`\n'
    )
    print("Info:")
    print(keysInfo.value)
    print()
    updateButton = gr.Button("Update", elem_classes=["mcww-hidden", "mcww-update-helpers-info-button"])
    @gr.on(
        triggers=[updateButton.click],
        outputs=[vramPlot, ramPlot],
        show_progress='hidden',
    )
    def onInfoTabUpdate():
        return comfyStats.getVramPlotUpdate(), comfyStats.getRamPlotUpdate()


