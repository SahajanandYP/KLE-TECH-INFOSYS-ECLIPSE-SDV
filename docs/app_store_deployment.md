# Apple App Store & Google Play Store Deployment Guide

This guide outlines the production deployment pipeline for the **Eclipse SDV Companion App** on iOS & Android.

---

## 1. Google Play Store Release (Android)

### Build Signed App Bundle (AAB):
```bash
cd mobile_app
flutter build appbundle --release
```
Artifact: `build/app/outputs/bundle/release/app-release.aab`

### Google Play Permissions Configured (`AndroidManifest.xml`):
- `BLUETOOTH_SCAN` & `BLUETOOTH_CONNECT` (Keyless entry)
- `ACCESS_FINE_LOCATION` (BLE proximity beacons)
- `INTERNET` (Cloud telematics via Central Jetson Hub)

---

## 2. Apple App Store Release (iOS)

### Build Signed iOS Archive (IPA):
```bash
cd mobile_app
flutter build ipa --release
```

### iOS Info.plist Privacy Keys:
- `NSBluetoothAlwaysUsageDescription`: "Eclipse SDV uses Bluetooth for keyless vehicle entry."
- `NSLocationWhenInUseUsageDescription`: "Used for vehicle location mapping and telematics."

---

## 3. Automated CI/CD (GitHub Actions / Fastlane)

Pushes to `main` automatically trigger multi-platform build and release to:
- **Google Play Internal Testing Track**
- **Apple TestFlight Beta Track**
