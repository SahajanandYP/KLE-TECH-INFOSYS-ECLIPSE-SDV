"""
Mobile Companion SDK (Eclipse SDV Client Library)
Used by iOS / Android / Flutter / React Native mobile applications to connect to the vehicle.
Supports:
1. Direct Local Mode (Wi-Fi / Bluetooth Low Energy / Local IP)
2. Cloud Telematics Mode (via Jetson Central Hub / Zenoh Broker)
"""

import json
import urllib.request
from typing import Dict, Any, Tuple, Optional

class MobileCompanionClient:
    def __init__(self, endpoint_url: str = "http://localhost:5000", auth_token: str = "SDV_SECURE_TOKEN_2026"):
        self.endpoint_url = endpoint_url.rstrip("/")
        self.auth_token = auth_token

    def send_command(self, action: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Sends an authenticated mobile command (LOCK, UNLOCK, HORN, HAZARD)."""
        url = f"{self.endpoint_url}/api/companion/command"
        payload = {
            "token": self.auth_token,
            "action": action
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("success", False), data.get("message", ""), data.get("data", {})
        except Exception as e:
            return False, f"Connection error: {e}", {}

    def unlock_vehicle(self) -> Tuple[bool, str]:
        success, msg, _ = self.send_command("UNLOCK")
        return success, msg

    def lock_vehicle(self) -> Tuple[bool, str]:
        success, msg, _ = self.send_command("LOCK")
        return success, msg

    def get_live_telemetry(self) -> Optional[Dict[str, Any]]:
        """Fetches speed, battery %, gear, and safety state."""
        url = f"{self.endpoint_url}/api/telemetry"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SDV-Mobile-App"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def get_opensovd_diagnostics(self) -> Optional[Dict[str, Any]]:
        """Fetches remote diagnostics (DTCs, software inventory)."""
        url = f"{self.endpoint_url}/api/diagnostics/sovd"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
