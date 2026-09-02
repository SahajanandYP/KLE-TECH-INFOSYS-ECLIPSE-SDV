#!/usr/bin/env python3
"""
Interactive VSS Mapping Configuration Helper
Used by vehicle operators during first-time vehicle onboarding.
"""

import os
import yaml
import json

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/vss_mapping.yaml"))

def show_current_mapping():
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found.")
        return
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
    print("\n=== Current Vehicle Profile ===")
    print(json.dumps(data.get("vehicle_profile", {}), indent=2))
    print("\n=== Active Signal Mappings ===")
    for rule in data.get("signal_mappings", []):
        print(f"  [{rule.get('can_id_hex', 'BUS')}] {rule['source_signal']} --> {rule['target_vss_path']} (Scale: {rule.get('scale', 1.0)})")

if __name__ == "__main__":
    show_current_mapping()
