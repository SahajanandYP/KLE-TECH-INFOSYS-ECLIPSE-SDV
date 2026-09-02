"""
Jetson Fleet & User Profile Admin Application (CLI / Terminal GUI)
Used on Jetson AGX Orin to inspect vehicle states, users, and digital keys.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from central_server.registry.registry_service import CentralVehicleRegistry
from central_server.registry.user_service import CentralUserService

def show_admin_dashboard():
    reg = CentralVehicleRegistry(storage_path="central_server/registry/vehicles.json")
    user_srv = CentralUserService(storage_path="central_server/registry/users.json")

    print("\n" + "=" * 65)
    print("      ECLIPSE SDV CENTRAL FLEET & USER MANAGEMENT (JETSON)       ")
    print("=" * 65)

    print("\n--- REGISTERED USERS & DIGITAL KEYS ---")
    users = user_srv.list_users()
    for u in users:
        print(f"  * [{u['role']}] {u['full_name']} ({u['email']})")
        print(f"    ID: {u['user_id']} | Vehicles: {', '.join(u['assigned_vehicle_ids'])}")
        print(f"    Key Token: {u['digital_key_token']} | Max Speed: {u['preferences']['max_speed_limit_kmh']} km/h\n")

    print("--- CONNECTED FLEET VEHICLES ---")
    vehicles = reg.list_vehicles()
    if not vehicles:
        print("  (No vehicles currently registered)")
    for v in vehicles:
        status_icon = "🟢" if v["status"] == "ONLINE" else "🔴"
        print(f"  {status_icon} Vehicle ID: {v['vehicle_id']} [{v['status']}]")
        print(f"    Name: {v['name']} ({v['model']} by {v['manufacturer']})")
        print(f"    Software: {v['software_inventory'].get('sdv_platform_version', 'N/A')} | Kernel: {v['software_inventory'].get('os_kernel', 'N/A')}")
        snap = v.get("current_state_snapshot", {})
        if snap:
            print(f"    Live State: Speed: {snap.get('speed_kmh', 0)} km/h | Battery: {snap.get('battery_soc_percent', 0)}% | Drive: {snap.get('drive_mode', 'N/A')}")
        print()
    print("=" * 65 + "\n")

if __name__ == "__main__":
    show_admin_dashboard()
