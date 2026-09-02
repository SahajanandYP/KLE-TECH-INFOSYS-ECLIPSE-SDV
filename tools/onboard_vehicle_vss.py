#!/usr/bin/env python3
"""
First-Time Vehicle Onboarding & VSS Calibration Wizard
Guides vehicle owners to calibrate physical CAN signals into standard COVESA VSS.
"""

import os
import yaml
import json

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/vss_mapping.yaml"))
CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/standard_vss_catalog.json"))

def run_onboarding_wizard():
    print("=" * 65)
    print("      ECLIPSE SDV VEHICLE ONBOARDING & VSS MAPPING WIZARD        ")
    print("=" * 65)
    print("Welcome! This wizard configures your vehicle's physical signals once.")
    print("After this, the SDV stack will auto-run on every vehicle boot.\n")

    print("Step 1: Choose Bus Interface Standard:")
    print("  [1] VIRYA APM Drive-by-Wire Skateboard (Default 500 kbps)")
    print("  [2] SAE J1939 Heavy Vehicle CAN Standard (250 / 500 kbps)")
    print("  [3] ISO 15031 Standard OBD-II Passenger Car CAN")
    print("  [4] Open EV Electric Battery / Motor CAN")
    print("  [5] Virtual Simulation (vcan0)")

    choice = input("\nSelect Profile [1-5, default 1]: ").strip() or "1"
    
    profile_names = {
        "1": ("virya-apm-01", "VIRYA APM Skateboard", "SocketCAN", "can0", 500000),
        "2": ("j1939-truck-01", "Commercial J1939 Vehicle", "SocketCAN", "can0", 250000),
        "3": ("obd2-car-01", "OBD-II Passenger Vehicle", "SocketCAN", "can0", 500000),
        "4": ("open-ev-01", "Open EV Powertrain", "SocketCAN", "can0", 500000),
        "5": ("sim-sdv-01", "Virtual Simulated Vehicle", "Simulation", "vcan0", 500000),
    }

    vid, vname, bus_type, iface, bitrate = profile_names.get(choice, profile_names["1"])

    config_data = {
        "vehicle_profile": {
            "id": vid,
            "name": vname,
            "model": "SDV-Production-2026",
            "manufacturer": "Eclipse SDV Partner",
            "bus_type": bus_type,
            "interface": iface,
            "bitrate": bitrate
        },
        "signal_mappings": [
            {"source_signal": "Vehicle_Speed", "target_vss_path": "Vehicle.Speed", "scale": 3.6, "unit": "km/h"},
            {"source_signal": "Battery_SoC", "target_vss_path": "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current", "scale": 1.0, "unit": "%"},
            {"source_signal": "Drive_Mode", "target_vss_path": "Vehicle.Powertrain.Transmission.CurrentGear", "value_map": {0: 0, 1: 1, 3: -1}},
            {"source_signal": "Emergency_Stop", "target_vss_path": "Vehicle.Safety.EStopActive", "scale": 1.0, "unit": "boolean"},
            {"source_signal": "Autonomous_DBW", "target_vss_path": "Vehicle.AutomatedDriving.IsActive", "scale": 1.0, "unit": "boolean"}
        ]
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config_data, f, indent=2, sort_keys=False)

    print(f"\n✅ VSS Mapping generated and saved to: {CONFIG_PATH}")
    print("=" * 65)
    print("Onboarding Complete! Your vehicle stack is now ready to auto-run on boot.")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_onboarding_wizard()
