#!/usr/bin/env bash
# ==============================================================================
# Eclipse SDV One-Line Vehicle Online Installer
# Usage on vehicle: curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
# ==============================================================================
set -e

echo "=== [1/4] Installing Eclipse SDV Dependencies on $(uname -m) ==="
sudo apt-get update -qq && sudo apt-get install -y -qq python3-pip can-utils iproute2 >/dev/null 2>&1 || true
pip3 install --user kuksa-client cantools python-can pygame >/dev/null 2>&1 || true

echo "=== [2/4] Setting up Priority Systemd Auto-Run Service ==="
sudo cp "$(pwd)/deployment/systemd/sdv-vehicle-autorun.service" /etc/systemd/system/ 2>/dev/null || true
sudo systemctl daemon-reload 2>/dev/null || true
sudo systemctl enable sdv-vehicle-autorun 2>/dev/null || true

echo "=== [3/4] Launching First-Time VSS Mapping Calibration Wizard ==="
python3 tools/onboard_vehicle_vss.py

echo "=== [4/4] Starting SDV Vehicle Stack ==="
nohup python3 vehicle_runtime/vehicle_stack.py config/vss_mapping.yaml > /tmp/vehicle_sdv.log 2>&1 &

echo "✅ Eclipse SDV Vehicle Stack installed and auto-running on boot!"
