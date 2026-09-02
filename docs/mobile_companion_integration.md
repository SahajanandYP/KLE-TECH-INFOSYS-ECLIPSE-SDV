# Mobile Companion App Integration Guide

## 1. Overview
The Eclipse SDV Mobile Companion enables smartphone users (iOS / Android) to authenticate, unlock/lock doors, monitor battery and speed, and trigger remote diagnostics.

```
+-------------------------------------------------------------------------------+
|                           SMARTPHONE (iOS / Android)                          |
|                 (Flutter / React Native / Native Swift/Kotlin)                |
+-------------------------------------------------------------------------------+
         |                                                   |
         | [Option A] Direct Wi-Fi / BLE                     | [Option B] Cloud / WAN Mode
         v                                                   v
+-------------------------------+                   +-------------------------------+
|  VEHICLE ONBOARD STACK        |                   |  JETSON CENTRAL REGISTRY      |
|  (:5000 / BLE GATT Service)   |                   |  (:8080 / Zenoh Cloud Broker) |
+-------------------------------+                   +-------------------------------+
```

---

## 2. Connection Modes

### Mode 1: Bluetooth Low Energy (BLE) / In-Proximity Keyless Entry
- **GATT Service UUID**: `0000sdv0-0000-1000-8000-00805f9b34fb`
- **Characteristics**:
  - `LockState` (Read/Notify): Reports `0x01` (Locked), `0x00` (Unlocked).
  - `AuthCommand` (Write): Accepts encrypted payload `{"token": "...", "action": "UNLOCK"}`.

### Mode 2: Local Wi-Fi / Direct REST & WebSocket
- Direct connection when smartphone is on the same local Wi-Fi / AP:
  - `POST http://<vehicle-ip>:5000/api/companion/command`
  - `GET http://<vehicle-ip>:5000/api/telemetry`

### Mode 3: Remote Cloud / Telematics (Zenoh / MQTT via Jetson)
- Connects from anywhere in the world through the Central Jetson Hub:
  - Mobile App $\rightarrow$ `https://<central-jetson-domain>/api/v1/vehicles/{id}`.

---

## 3. Flutter Example Integration Snippet

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class SDVCompanionService {
  final String vehicleUrl = "http://192.168.1.105:5000";
  final String authToken = "SDV_SECURE_TOKEN_2026";

  Future<bool> unlockVehicle() async {
    final response = await http.post(
      Uri.parse("$vehicleUrl/api/companion/command"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"token": authToken, "action": "UNLOCK"}),
    );
    return response.statusCode == 200;
  }
}
```
