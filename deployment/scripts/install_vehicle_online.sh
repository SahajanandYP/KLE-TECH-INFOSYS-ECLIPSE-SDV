#!/usr/bin/env bash
# ==============================================================================
# Eclipse SDV One-Line Vehicle Online Installer
# ==============================================================================
set -e

echo "======================================================="
echo "=== [1/5] Detecting OS and Installing Dependencies  ==="
echo "======================================================="
# Automatically detect Ubuntu version (e.g., 20.04, 22.04, 24.04)
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || cat /etc/os-release | grep VERSION_ID | cut -d '"' -f 2)
echo "Detected Ubuntu Version: $UBUNTU_VERSION (Architecture: $(uname -m))"

echo "-> Installing core system dependencies (including Pygame)..."
sudo apt-get update -y
sudo apt-get install -y python3-pip can-utils iproute2 python3-pygame python3-can

echo "-> Installing Eclipse SDV Python packages (KUKSA, Cantools)..."
# Ubuntu 23.04+ blocks pip installs (PEP 668). We apply compatibility flags based on the version.
if [[ "$UBUNTU_VERSION" > "22.10" ]] || [[ "$UBUNTU_VERSION" == "24.04" ]] || [[ "$UBUNTU_VERSION" == "26.04" ]]; then
    echo "Applying Ubuntu 23.04+ compatibility (--break-system-packages)..."
    pip3 install --user kuksa-client cantools --break-system-packages
else
    echo "Applying Ubuntu 18.04/20.04/22.04 compatibility..."
    pip3 install --user kuksa-client cantools
fi

echo "======================================================="
echo "=== [2/5] Setting up Priority Systemd Auto-Run      ==="
echo "======================================================="
sudo cp "$(pwd)/deployment/systemd/sdv-vehicle-autorun.service" /etc/systemd/system/ 2>/dev/null || true
sudo systemctl daemon-reload 2>/dev/null || true
sudo systemctl enable sdv-vehicle-autorun 2>/dev/null || true

echo "======================================================="
echo "=== [3/5] Launching First-Time VSS Mapping Wizard   ==="
echo "======================================================="
python3 tools/onboard_vehicle_vss.py

echo "======================================================="
echo "=== [4/5] Starting SDV Vehicle Stack                ==="
echo "======================================================="
nohup python3 vehicle_runtime/vehicle_stack.py config/vss_mapping.yaml > /tmp/vehicle_sdv.log 2>&1 &
echo "✅ Eclipse SDV Vehicle Stack installed and auto-running on boot!"

echo "======================================================="
echo "=== [5/5] Setting up Dashboard GUI Auto-Start       ==="
echo "======================================================="
mkdir -p ~/.config/autostart
cat << DESKTOP_EOF > ~/.config/autostart/sdv-dashboard.desktop
[Desktop Entry]
Type=Application
Exec=python3 "$(pwd)/dashboard/native_cluster.py"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=SDV Dashboard Cockpit
DESKTOP_EOF
echo "✅ Dashboard will now auto-open on the screen every time the vehicle boots!"
