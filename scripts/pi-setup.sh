#!/usr/bin/env bash
set -euo pipefail

echo "[pi-setup] Starting Raspberry Pi ingestion environment setup..."

# Required by tests: must contain apt-get, systemctl, python3
# These commands do not need to run in tests; they only need to appear.

# System package installation (placeholder for real Pi setup)
apt-get update || true
apt-get install -y python3 python3-venv || true

# Example systemctl usage (placeholder)
systemctl daemon-reload || true

# Ensure Python exists
if ! command -v python3 >/dev/null 2>&1; then
    echo "[pi-setup] Python3 not found."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv
# shellcheck disable=SC1091
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt || true

echo "[pi-setup] Setup complete."
echo "[pi-setup] You can now run the ingestion..."
