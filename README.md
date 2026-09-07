# 🚗 Eclipse SDV: VIRYA APM Autonomous Skateboard

Welcome to the **Software Defined Vehicle (SDV)** stack for the VIRYA APM Skateboard. This project transforms a bare-metal hardware chassis into a fully connected, cloud-native, OTA-updatable smart vehicle using official **COVESA / Eclipse SDV** global automotive standards.

---

## 🌟 Core Features & Accomplishments

### 1. True Hardware Integration (CAN Bus Decoder)
We bypassed simulations and integrated directly with the physical hardware. The Python background engine actively reads the `can0` interface, decrypts the proprietary **0x1291 J1939 CAN frame**, and extracts the true Traction Battery (SOC%), Drive Mode, E-Stop status, and Vehicle Speed in real-time.

### 2. Cinematic Digital Cockpit (Dashboard)
We designed an ultra-minimalist, Tesla/Vercel-inspired Digital Instrument Cluster (`dashboard/native_cluster.py`) featuring:
- Fullscreen immersive UI with pure black aesthetics.
- A 6-second cinematic boot sequence fading between Eclipse SDV, Infosys, and KLE Tech logos.
- Live tracking of Speed, Battery, and Gear.
- **Smart Driver Prompts**: Yellow/Blue banners for Over-The-Air (OTA) update approvals.

### 3. Edge-to-Cloud Fleet Command (Jetson Hub)
The Skateboard is fully networked to a centralized **Jetson Hub Fleet Manager** (`central_server/native_fleet_app.py`).
- **Live Registry**: The moment the Skateboard boots, it registers its IP and telemetry to the cloud.
- **Fleet UI**: Operators can monitor all vehicles simultaneously.
- **One-Click Actions**: Push global OTA updates or pull remote diagnostics with a single click.

### 4. True Over-The-Air (OTA) Updates
We engineered a complete, production-grade OTA lifecycle without manual terminal commands.
- The Jetson Hub beams an update signal via **Eclipse Zenoh** (or auto-fallback HTTP).
- The Skateboard Dashboard drops a UI banner: `[ENTER] Update Now | [ESC] Update Later`.
- Upon approval, the vehicle autonomously runs a `git pull` and safely **hot-reloads its Linux engine in-place** without shutting down the physical computer.

### 5. Mobile Companion App & Remote Diagnostics
A mobile-responsive Web App (`web_app/index.html`) allowing the driver's phone to connect via the **Native Web Bluetooth API**. 
We also implemented **Eclipse OpenSOVD** (Service-Oriented Vehicle Diagnostics), allowing the Jetson Hub to instantly pull simulated Diagnostic Trouble Codes (DTCs) like *P0A7F (Battery Over-temp)* over the cloud, completely replacing physical mechanic OBD-II scanners.

---

## 🧩 Eclipse SDV Standards Implemented

This project is built on the shoulders of giants. Here is how we utilized the official Eclipse Foundation architecture:

1. **Eclipse KUKSA**: Acts as the vehicle's central nervous system/databroker, translating raw hexadecimal CAN bytes into clean, readable software APIs.
2. **Eclipse VSS (Vehicle Signal Specification)**: Standardizes our data dictionary (e.g., `Vehicle.Powertrain.TractionBattery.StateOfCharge.Current`).
3. **Eclipse Zenoh**: Provides the ultra-fast Edge-to-Cloud Publish/Subscribe networking protocol, allowing IP-less OTA broadcasts.
4. **Eclipse OpenSOVD**: Defines the architecture for our Remote Diagnostics reporting.
5. **Eclipse Velocitas**: Inspired the microservice-based Python architecture of our `applications/` folder.
6. **Eclipse Kanto / Leda**: Their container orchestration logic is natively simulated in our `ota_manager_app.py` lifecycle.

---

## 🚀 Quick Start Runbook

### On the Jetson Hub (Cloud / Command Center)
Start the central cloud server and the Fleet UI:
```bash
sudo pkill -f server.py
python3 central_server/server.py &
python3 central_server/native_fleet_app.py
```

### On the VIRYA Skateboard (The Vehicle)
Turn on the physical CAN hardware and start the vehicle engine and dashboard:
```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
sudo systemctl restart sdv-vehicle-autorun
python3 dashboard/native_cluster.py
```

*(Note: The vehicle background engine automatically starts on boot via `systemd`. You only need to run the dashboard command to see the UI).*
