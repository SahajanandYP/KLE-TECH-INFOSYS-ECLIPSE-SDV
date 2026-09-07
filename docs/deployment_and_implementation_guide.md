# 🛠️ Eclipse SDV: Complete End-to-End Implementation Guide

This guide is designed for engineers and technicians. It provides the exact, step-by-step instructions to implement the Eclipse SDV platform on physical hardware (e.g., an NVIDIA Jetson AGX Orin connected to a vehicle/skateboard) and deploy the mobile app.

---

## 📋 Phase 0: Hardware & Network Preparation

1. **The Vehicle Edge Node (e.g., Jetson AGX Orin / Raspberry Pi):**
   - Must have Ubuntu Linux (20.04 or 22.04 LTS).
   - Must have an internet connection (Wi-Fi or Ethernet).
2. **Physical CAN Connection:**
   - Connect your CAN transceiver (e.g., PCAN-USB or native Jetson CAN headers) to the vehicle's CAN bus.
   - Bring up the CAN interface in Linux:
     ```bash
     sudo ip link set can0 type can bitrate 500000
     sudo ip link set up can0
     ```
3. **The Central Server Node (Can be the same Jetson or a Cloud VM):**
   - Must have a static IP address or a known hostname so vehicles can find it.

---

## ☁️ Phase 1: Implement the Central Server (The "Brain")

If you are running the Fleet Manager on your Jetson desktop, follow these steps to start the central infrastructure.

1. **Open a terminal on the server machine.**
2. **Navigate to the SDV project folder:**
   ```bash
   cd "/home/nvidia/Desktop/Eclipse SDV"
   ```
3. **Start the Central Fleet Registry & API:**
   ```bash
   python3 central_server/server.py
   ```
   *Result:* The server is now running on port `8080` and waiting for vehicles to connect.

---

## 🚘 Phase 2: Implement the Vehicle Software (The "Car")

Now, move to the terminal of the computer that is physically attached to the vehicle (if this is an all-in-one Jetson, just open a new terminal window).

1. **Run the One-Line Automated Installer:**
   This installs all Eclipse dependencies (KUKSA, python-can) and configures Linux `systemd`.
   ```bash
   bash deployment/scripts/install_vehicle_online.sh
   ```

2. **Run the Signal Mapping Wizard (Translation Layer):**
   This tells the software how to read your specific vehicle's CAN bus.
   ```bash
   python3 tools/onboard_vehicle_vss.py
   ```
   - When prompted, select your vehicle type (e.g., `[1]` for VIRYA APM Drive-by-Wire, or `[5]` for Virtual Simulation).
   - *Result:* A file named `config/vss_mapping.yaml` is generated.

3. **Start the Vehicle Software Stack:**
   (Note: If you reboot the Jetson, `systemd` will do this automatically, but for the first time, you can run it manually to see the logs).
   ```bash
   python3 vehicle_runtime/vehicle_stack.py config/vss_mapping.yaml
   ```
   *Result:* The Eclipse KUKSA databroker starts, reads the CAN bus, runs the 5 Velocitas apps, and registers with the Central Server from Phase 1.

---

## 🖥️ Phase 3: Implement the Driver's Dashboard

The vehicle is running, but the driver needs a screen. Connect an HDMI monitor to the Jetson.

1. **Open a new terminal.**
2. **Launch the Native Instrument Cluster:**
   ```bash
   python3 dashboard/native_cluster.py
   ```
   *Result:* The screen will go dark, show the **Eclipse SDV / Infosys / KLE Tech** boot-up splash, perform a gauge needle sweep self-test, and then display the live 60 FPS speedometer and battery gauge.

---

## 📱 Phase 4: Implement the Mobile Companion App

You can deploy the app to an actual iPhone/Android, or run a simulator.

### Option A: Build for a Physical Smartphone (Android)
Ensure you have the [Flutter SDK installed](https://docs.flutter.dev/get-started/install/linux).
1. **Navigate to the mobile app folder:**
   ```bash
   cd "/home/nvidia/Desktop/Eclipse SDV/mobile_app"
   ```
2. **Build the Android APK:**
   ```bash
   flutter build apk --release
   ```
3. Transfer the APK (`build/app/outputs/flutter-apk/app-release.apk`) to your phone and install it. Connect it to the Jetson's IP address in the app settings.

### Option B: Run the Terminal-Based Simulator
If you don't want to install Flutter right now, you can test the mobile API directly from the Jetson:
1. **Open a new terminal:**
   ```bash
   python3 mobile_bridge/mobile_simulator.py http://localhost:5000
   ```
2. Type commands like `unlock` or `aeb` (Emergency Brake) and watch the Dashboard screen (from Phase 3) react instantly!

---

## ✅ Implementation Checklist Complete
You have successfully:
1. Started the Cloud Server.
2. Wired and Installed the Vehicle Edge Stack.
3. Booted the UI Cockpit Dashboard.
4. Connected the Mobile App.
