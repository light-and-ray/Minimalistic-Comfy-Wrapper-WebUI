#!/bin/bash
set -e
cd "$(dirname "$0")"
. venv/bin/activate
set -x
python -m mcww.workflowConverting "$@"
