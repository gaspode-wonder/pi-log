#!/usr/bin/env bash
set -euo pipefail

PI_HOST="pi@raspberrypi.local"
PI_DIR="/opt/pi-log"

echo "Syncing code to Pi..."
rsync -av --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    ./ "$PI_HOST:$PI_DIR/"

echo "Installing dependencies..."
ssh "$PI_HOST" "cd $PI_DIR && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"

echo "Reloading systemd..."
ssh "$PI_HOST" "sudo systemctl daemon-reload"

echo "Restarting service..."
ssh "$PI_HOST" "sudo systemctl restart pi-log.service"

echo "Deployment complete."
