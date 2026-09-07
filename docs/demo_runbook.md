# 🚀 Eclipse SDV Platform: Official Demo Runbook

This guide will walk you through a flawless live demonstration of the entire platform from scratch. 
You will need to open **4 separate terminal windows** on the Jetson to run the different components simultaneously.

---

## 🛠️ Step 1: Start the Central Jetson Server (The Cloud/Fleet Hub)
*Open Terminal 1*

This represents your cloud backend and fleet manager. It listens for incoming vehicle connections and tracks driver profiles.

```bash
cd "/home/nvidia/Desktop/Eclipse SDV"
python3 central_server/server.py
```
*(Leave this running in the background. You will see it listening on port 8080).*

---

## 🚘 Step 2: First-Time Vehicle Setup (The Onboarding Wizard)
*Open Terminal 2*

This represents a factory worker or operator configuring a brand new vehicle for the first time.

```bash
cd "/home/nvidia/Desktop/Eclipse SDV"
python3 tools/onboard_vehicle_vss.py
```
1. You will be prompted to select a vehicle bus profile.
2. Type `5` and hit Enter (Virtual Simulated Vehicle).
3. The wizard will successfully map the signals and generate `config/vss_mapping.yaml`.

---

## ⚡ Step 3: Power On the Vehicle (Start the SDV Stack)
*Still in Terminal 2*

Now that the vehicle is configured, simulate turning the ignition on. This script automatically runs all 5 Velocitas use cases and the KUKSA databroker.

```bash
python3 vehicle_runtime/vehicle_stack.py config/vss_mapping.yaml
```
*(You will see logs showing the vehicle successfully registering with the Central Jetson Server, and the 5 use cases coming online).*

---

## 🖥️ Step 4: Show the Driver's Instrument Cluster
*Open Terminal 3*

This is the hardware-accelerated screen the driver sees behind the steering wheel.

```bash
cd "/home/nvidia/Desktop/Eclipse SDV"
python3 dashboard/native_cluster.py
```
**What to point out to the audience:**
1. The immediate boot splash showing **Eclipse SDV, Infosys, and KLE Tech**.
2. The authentic automotive **gauge needle sweep** (0 ➔ 60 ➔ 0 km/h).
3. The live 60 FPS telemetry updating in real-time.

---

## 📱 Step 5: The Mobile Companion App (User's Phone)
*Open Terminal 4 (or just use the browser)*

Show the audience how the owner interacts with the vehicle remotely.

**Option A (Terminal Simulator):**
```bash
cd "/home/nvidia/Desktop/Eclipse SDV"
python3 mobile_bridge/mobile_simulator.py http://localhost:5000
```
*Try typing `lock`, `unlock`, `ota`, or `aeb` in the terminal and watch the cluster screen react instantly!*

**Option B (Interactive UI Demo):**
Open the provided `mobile_companion.html` file in a web browser to show off the smooth Flutter-style UI, tapping the lock button to trigger haptics.

---

## 👑 Bonus: The Fleet Manager View
*Open a final Terminal*

Show the audience what the fleet administrator sees on the Jetson dashboard:

```bash
cd "/home/nvidia/Desktop/Eclipse SDV"
python3 central_server/admin_app.py
```
*(This will print a clean summary showing the vehicle is `ONLINE`, reporting its current speed, battery %, and software version to the cloud).*
