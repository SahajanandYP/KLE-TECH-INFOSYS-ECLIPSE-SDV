"""
Bluetooth Low Energy (BLE) Proximity & Keyless Entry Handler
Detects smartphone RSSI proximity and triggers hands-free unlock when within range (< 3m).
"""

import time
import logging
from typing import Callable, Optional

logger = logging.getLogger("BLEProximityHandler")

class BLEProximityHandler:
    def __init__(self, on_proximity_unlock: Optional[Callable[[], None]] = None, rssi_threshold_dbm: int = -65):
        self.on_proximity_unlock = on_proximity_unlock
        self.rssi_threshold_dbm = rssi_threshold_dbm # Approx 2-3 meters
        self.is_paired = False
        self.last_rssi = -100

    def simulate_ble_scan_step(self, rssi_dbm: int) -> bool:
        """Processes RSSI signal strength from authorized mobile device."""
        self.last_rssi = rssi_dbm
        if rssi_dbm >= self.rssi_threshold_dbm:
            logger.info(f"BLE Proximity Trigger: Mobile detected nearby ({rssi_dbm} dBm). Actuating Keyless Unlock.")
            if self.on_proximity_unlock:
                self.on_proximity_unlock()
            return True
        return False
