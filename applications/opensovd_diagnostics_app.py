"""
Use Case 3: Remote Diagnostics via OpenSOVD (ISO 17978 RESTful API)
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("OpenSOVDDiagnosticsApp")

class OpenSOVDDiagnosticsApp:
    def __init__(self, vss_broker, software_inventory: Dict[str, Any]):
        self.vss_broker = vss_broker
        self.software_inventory = software_inventory
        self.active_dtcs: List[str] = []

    def inject_dtc(self, dtc_code: str):
        if dtc_code not in self.active_dtcs:
            self.active_dtcs.append(dtc_code)

    def clear_dtcs(self):
        self.active_dtcs = []

    def get_sovd_diagnostics(self) -> Dict[str, Any]:
        signals = self.vss_broker.get_all_signals()
        return {
            "protocol": "ISO_17978_OpenSOVD",
            "version": "1.0.0",
            "software_inventory": self.software_inventory,
            "active_faults_dtc": self.active_dtcs,
            "safety_interlocks": {
                "estop_tripped": signals.get("Vehicle.Safety.EStopActive", False),
                "interlock_active": signals.get("Vehicle.Safety.InterlockEngaged", False)
            },
            "vss_tree_snapshot": signals
        }
