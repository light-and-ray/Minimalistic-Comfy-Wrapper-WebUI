#!/bin/bash
set -e
cd "$(dirname "$0")"
. venv/bin/activate
set -x
. .env
cd src
python main.py
