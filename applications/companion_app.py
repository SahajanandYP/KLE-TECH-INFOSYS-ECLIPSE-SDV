"""
Use Case 1: Companion Lock / Unlock Application (Eclipse Velocitas Pattern)
Handles authenticated mobile commands, operates digital latch, and confirms state.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("CompanionApp")

class CompanionLockApp:
    def __init__(self, vss_broker):
        self.vss_broker = vss_broker
        self.is_locked = True
        self.door_open = False
        self.sync_to_vss()

    def sync_to_vss(self):
        self.vss_broker.set_signal("Vehicle.Cabin.Door.Row1.Left.IsLocked", self.is_locked)
        self.vss_broker.set_signal("Vehicle.Cabin.Door.Row1.Left.IsOpen", self.door_open)

    def execute_command(self, auth_token: str, action: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Executes authenticated companion action."""
        if not auth_token or auth_token != "SDV_SECURE_TOKEN_2026":
            return False, "AUTHENTICATION_FAILED: Invalid token.", {}

        if action == "UNLOCK":
            self.is_locked = False
            self.door_open = True
            logger.info("Companion Command: Vehicle UNLOCKED.")
        elif action == "LOCK":
            self.is_locked = True
            self.door_open = False
            logger.info("Companion Command: Vehicle LOCKED.")
        else:
            return False, f"UNKNOWN_ACTION: {action}", {}

        self.sync_to_vss()
        status_data = {
            "is_locked": self.is_locked,
            "door_open": self.door_open,
            "vss_path": "Vehicle.Cabin.Door.Row1.Left.IsLocked",
            "confirmed": True
        }
        return True, f"SUCCESS: Vehicle {action}ED.", status_data
