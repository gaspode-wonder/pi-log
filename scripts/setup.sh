#!/usr/bin/env bash
set -e

echo "[pi-log] Installing..."

# Directories
sudo mkdir -p /opt/geiger
sudo mkdir -p /var/lib/geiger
sudo mkdir -p /etc/default

# Copy code
sudo cp geiger_pi_reader.py /opt/geiger/
sudo chmod +x /opt/geiger/geiger_pi_reader.py

# Install requirements
if [ -f requirements.txt ]; then
    sudo pip3 install -r requirements.txt
fi

# Install environment file if missing
if [ ! -f /etc/default/geiger ]; then
    sudo cp config/example.env /etc/default/geiger
fi

# Install systemd service
sudo cp systemd/geiger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable geiger.service
sudo systemctl restart geiger.service

echo "[pi-log] Installation complete."
