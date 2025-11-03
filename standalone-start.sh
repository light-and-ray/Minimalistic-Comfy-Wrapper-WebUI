#!/bin/bash
set -e
cd "$(dirname "$0")"

while true; do
    . venv/bin/activate
    python -m mcww.standalone "$@"

    if [ ! -f "./RESTART_REQUESTED" ]; then
        break
    fi

    rm -f "./RESTART_REQUESTED"
done
