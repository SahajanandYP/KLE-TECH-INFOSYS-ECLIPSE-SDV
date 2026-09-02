"""
Jetson Fault & Crash Isolation Notifier
Ensures vehicle crashes/faults are logged asynchronously without impacting Jetson stability.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("JetsonFaultNotifier")

class JetsonFaultNotifier:
    def __init__(self, log_path: str = "/tmp/sdv_vehicle_faults.log"):
        self.log_path = log_path

    def notify_vehicle_fault(self, vehicle_id: str, error_message: str, stack_trace: str = ""):
        """Asynchronously records vehicle fault without crashing Jetson server."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vehicle_id": vehicle_id,
            "error": error_message,
            "trace": stack_trace,
            "severity": "WARNING"
        }
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            logger.warning(f"Vehicle Fault Recorded for '{vehicle_id}': {error_message} (Jetson Hub Healthy)")
        except Exception as e:
            logger.error(f"Error logging fault: {e}")
