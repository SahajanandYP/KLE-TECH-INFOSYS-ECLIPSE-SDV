# Mobile App Installation & Vehicle Connection Guide

---

## 📱 Step 1: Install the Mobile App on Smartphone

### For Android:
1. Scan the Vehicle Dashboard QR Code or download `app-release.apk`.
2. Tap **Install** (Allow installation from trusted sources).

### For iOS (iPhone):
1. Open the TestFlight invitation link or scan QR code.
2. Tap **Install Eclipse SDV Companion**.

---

## 🔗 Step 2: Connect Mobile App to Vehicle (Dual Mode)

```
                 HOW TO CONNECT TO YOUR VEHICLE
                 ==============================

  [NEAR VEHICLE (< 3m)]                [REMOTE / ANYWHERE IN WORLD]
  Mode: Bluetooth Low Energy (BLE)     Mode: Remote Cloud Telematics
  * Automatic Keyless Discovery        * Connects via Central Jetson Hub
  * Hands-free Lock / Unlock           * Live Battery %, Speed, Remote Lock
```

### Option A: Automatic Bluetooth Proximity (Near Vehicle)
1. Turn on Bluetooth on your smartphone.
2. Walk within 3 meters of the vehicle.
3. The app automatically pairs with **"Eclipse-SDV-APM"** and enables instant keyless entry.

### Option B: Remote Cloud Connection (Over Internet)
1. Open the App Settings (Gear Icon ⚙️).
2. Enter the Central Jetson Hub address: `https://<jetson-ip-or-domain>:8080`.
3. Enter your Driver Digital Key Token (e.g. `SDV_SECURE_TOKEN_2026`).
4. Tap **Connect** ➔ You can now monitor battery and lock/unlock from anywhere!
