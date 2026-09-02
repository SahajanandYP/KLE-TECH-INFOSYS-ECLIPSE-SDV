"""
Generic Mock Vehicle Adapter & Dynamics Simulator
Provides dynamic VSS telemetry without requiring physical vehicle hardware.
"""

import time
import math
import random
from datetime import datetime, timezone
from typing import Dict, Any

from vehicle_adapters.base.adapter_interface import (
    BaseVehicleAdapter,
    VehicleProfile,
    VehicleStateSnapshot
)

class MockVehicleAdapter(BaseVehicleAdapter):
    def __init__(self, profile: VehicleProfile):
        super().__init__(profile)
        self.current_speed_kmh = 0.0
        self.battery_soc = 95.0
        self.current_gear = 1 # 1: D, 0: N, -1: R
        self.drive_mode = "FORWARD"
        self.autonomous_active = True
        self.emergency_stop = False
        self.interlock = False
        self.charging = False
        self.time_step = 0.0

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def step_simulation(self, dt: float = 0.5):
        """Simulates vehicle driving cycle."""
        self.time_step += dt
        # Smooth sinusoidal speed profile bounded by max speed
        target_speed = (math.sin(self.time_step / 10.0) + 1.0) / 2.0 * min(self.profile.max_speed_kmh, 45.0)
        # Acceleration smoothing
        self.current_speed_kmh += (target_speed - self.current_speed_kmh) * 0.2
        self.current_speed_kmh = max(0.0, round(self.current_speed_kmh, 2))

        # Battery slow discharge based on speed
        discharge_rate = (0.005 + (self.current_speed_kmh / 100.0) * 0.02) * dt
        self.battery_soc = max(5.0, round(self.battery_soc - discharge_rate, 2))

        if self.current_speed_kmh > 0.5:
            self.current_gear = 1
            self.drive_mode = "FORWARD"
        else:
            self.current_gear = 0
            self.drive_mode = "NEUTRAL"

    def read_vss_signals(self) -> Dict[str, Any]:
        self.step_simulation()
        return {
            "Vehicle.Speed": self.current_speed_kmh,
            "Vehicle.Powertrain.Transmission.CurrentGear": self.current_gear,
            "Vehicle.Powertrain.Transmission.DriveMode": self.drive_mode,
            "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": self.battery_soc,
            "Vehicle.AutomatedDriving.IsActive": self.autonomous_active,
            "Vehicle.Safety.EStopActive": self.emergency_stop,
            "Vehicle.Safety.InterlockEngaged": self.interlock,
            "Vehicle.Powertrain.TractionBattery.Charging.IsConnected": self.charging
        }

    def get_state_snapshot(self) -> VehicleStateSnapshot:
        vss = self.read_vss_signals()
        return VehicleStateSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_online=self.is_connected,
            speed_kmh=self.current_speed_kmh,
            drive_mode=self.drive_mode,
            current_gear=self.current_gear,
            battery_soc_percent=self.battery_soc,
            autonomous_active=self.autonomous_active,
            emergency_stop_active=self.emergency_stop,
            interlock_engaged=self.interlock,
            charging_connected=self.charging,
            active_dtcs=[],
            raw_vss_signals=vss
        )
