#!/usr/bin/env python3
"""
Interactive Smartphone Mobile Companion Simulator
Simulates an iPhone / Android App sending companion commands and displaying telemetry.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from mobile_bridge.mobile_client_sdk import MobileCompanionClient

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    client = MobileCompanionClient(endpoint_url=target)

    print("==================================================")
    print("      ECLIPSE SDV SMARTPHONE COMPANION APP        ")
    print("==================================================")
    print(f"Target Vehicle: {target}")
    
    # 1. Fetch live telemetry
    telemetry = client.get_live_telemetry()
    if telemetry:
        print("\n--- Live Vehicle Status ---")
        print(f"  Speed:    {telemetry.get('speed_kmh')} km/h")
        print(f"  Battery:  {telemetry.get('battery_soc_percent')}%")
        print(f"  DBW Mode: {'ACTIVE' if telemetry.get('dbw_active') else 'MANUAL'}")
        print(f"  Health:   {telemetry.get('ecu_health')}")
    else:
        print("\n[Warning] Vehicle offline or unreachable.")

    # 2. Test Unlock Action
    print("\n[User Action] Tapping 'UNLOCK VEHICLE' on Phone Screen...")
    success, msg = client.unlock_vehicle()
    print(f"Result: {msg}")

    # 3. Test Lock Action
    print("\n[User Action] Tapping 'LOCK VEHICLE' on Phone Screen...")
    success, msg = client.lock_vehicle()
    print(f"Result: {msg}")
    print("==================================================")

if __name__ == "__main__":
    main()
