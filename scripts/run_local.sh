#!/usr/bin/env bash
set -euo pipefail

# Activate venv if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python run.py
