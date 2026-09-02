"""
Use Case 5: AI-Assisted Emergency Braking Application
Detects obstacle distance and commands automatic safe stop through VSS layer.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("EmergencyBrakingApp")

class EmergencyBrakingApp:
    def __init__(self, vss_broker, brake_distance_threshold_m: float = 2.0):
        self.vss_broker = vss_broker
        self.brake_distance_threshold_m = brake_distance_threshold_m
        self.aeb_active = False

    def process_obstacle_telemetry(self, distance_meters: float) -> Tuple[bool, str]:
        """Evaluates obstacle distance against current vehicle speed."""
        current_speed = self.vss_broker.get_signal("Vehicle.Speed") or 0.0

        if distance_meters <= self.brake_distance_threshold_m and current_speed > 0.5:
            self.aeb_active = True
            logger.warning(f"AEB TRIGGERED! Obstacle at {distance_meters}m (Speed: {current_speed} km/h). Commanding Emergency Stop.")
            # Command brake deceleration via VSS
            self.vss_broker.set_signal("Vehicle.Chassis.Brake.PedalPosition", 100.0)
            self.vss_broker.set_signal("Vehicle.Speed", 0.0)
            self.vss_broker.set_signal("Vehicle.Safety.Braking.LLCStop", True)
            return True, f"EMERGENCY_BRAKE_ACTIVATED: Stopped vehicle from {current_speed} km/h."
        else:
            self.aeb_active = False
            self.vss_broker.set_signal("Vehicle.Chassis.Brake.PedalPosition", 0.0)
            self.vss_broker.set_signal("Vehicle.Safety.Braking.LLCStop", False)
            return False, "NORMAL: Path clear."
