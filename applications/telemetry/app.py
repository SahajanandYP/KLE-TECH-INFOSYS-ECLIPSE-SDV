"""
Eclipse Velocitas Telemetry Application
Vehicle-agnostic telemetry consumer that streams normalized VSS vehicle data.
"""

import json
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger("VelocitasTelemetryApp")

class VelocitasTelemetryApp:
    def __init__(self, publish_fn: Callable[[str, Dict[str, Any]], None] = None):
        self.publish_fn = publish_fn or (lambda topic, data: logger.info(f"[{topic}]: {json.dumps(data)}"))

    def on_vss_update(self, path: str, value: Any):
        """Called whenever a subscribed VSS signal updates."""
        if path in ("Vehicle.Speed", "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current"):
            telemetry_packet = {
                "signal": path,
                "value": value,
                "type": "METRIC"
            }
            self.publish_fn("telemetry/metrics", telemetry_packet)
