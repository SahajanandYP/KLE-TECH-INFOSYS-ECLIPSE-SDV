"""
Use Case 2: Vehicle Status & Telemetry Dashboard App
Aggregates live speed, battery, steer angle, DBW mode, and ECU health.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("TelemetryDashboardApp")

class TelemetryDashboardApp:
    def __init__(self, vss_broker):
        self.vss_broker = vss_broker

    def get_dashboard_telemetry(self) -> Dict[str, Any]:
        signals = self.vss_broker.get_all_signals()
        return {
            "speed_kmh": signals.get("Vehicle.Speed", 0.0),
            "battery_soc_percent": signals.get("Vehicle.Powertrain.TractionBattery.StateOfCharge.Current", 100.0),
            "gear": signals.get("Vehicle.Powertrain.Transmission.CurrentGear", 0),
            "steering_angle_deg": signals.get("Vehicle.Chassis.SteeringWheel.Angle", 0.0),
            "dbw_active": signals.get("Vehicle.AutomatedDriving.IsActive", False),
            "estop_active": signals.get("Vehicle.Safety.EStopActive", False),
            "ecu_health": "OPTIMAL" if not signals.get("Vehicle.Safety.EStopActive") else "ESTOP_ENGAGED"
        }
