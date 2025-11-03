#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        venv_python = os.path.join(script_dir, "venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(script_dir, "venv", "bin", "python")
    restart_file = os.path.join(script_dir, "RESTART_REQUESTED")
    os.chdir(script_dir)

    while True:
        try:
            result = subprocess.run(
                [venv_python, "-m", "mcww.standalone"] + sys.argv[1:],
                check=False
            )
        except KeyboardInterrupt:
            pass
        if not os.path.exists(restart_file):
            break
        os.remove(restart_file)

if __name__ == "__main__":
    main()
