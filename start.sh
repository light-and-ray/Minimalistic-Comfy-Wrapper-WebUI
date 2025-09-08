#!/bin/bash
set -ex
cd "$(dirname "$0")"
. .venv/bin/activate
. .env
cd src
python main.py
