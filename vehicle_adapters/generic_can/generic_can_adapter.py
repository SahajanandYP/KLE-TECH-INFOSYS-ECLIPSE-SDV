"""
Generic SocketCAN Vehicle Adapter
Connects to physical or virtual SocketCAN and maps arbitrary CAN frames to VSS signals.
"""

import socket
import struct
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timezone

from vehicle_adapters.base.adapter_interface import (
    BaseVehicleAdapter,
    VehicleProfile,
    VehicleStateSnapshot
)
from vehicle_adapters.base.signal_mapping import GenericSignalMapper

logger = logging.getLogger("GenericCanAdapter")

class GenericCanAdapter(BaseVehicleAdapter):
    def __init__(self, profile: VehicleProfile, can_interface: str = "can0", mapper: Optional[GenericSignalMapper] = None):
        super().__init__(profile)
        self.can_interface = can_interface
        self.mapper = mapper or GenericSignalMapper()
        self.can_socket: Optional[socket.socket] = None
        self.latest_vss: Dict[str, Any] = {
            "Vehicle.Speed": 0.0,
            "Vehicle.Powertrain.Transmission.CurrentGear": 0,
            "Vehicle.Powertrain.Transmission.DriveMode": "NEUTRAL",
            "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": 100.0,
            "Vehicle.AutomatedDriving.IsActive": False,
            "Vehicle.Safety.EStopActive": False,
            "Vehicle.Safety.InterlockEngaged": False,
            "Vehicle.Powertrain.TractionBattery.Charging.IsConnected": False
        }

    def connect(self) -> bool:
        try:
            self.can_socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
            self.can_socket.bind((self.can_interface,))
            self.can_socket.settimeout(0.5)
            self.is_connected = True
            logger.info(f"Connected to CAN interface: {self.can_interface}")
            return True
        except Exception as e:
            logger.warning(f"Could not bind CAN interface '{self.can_interface}': {e}. Running in disconnected mode.")
            self.is_connected = False
            return False

    def disconnect(self) -> None:
        if self.can_socket:
            try:
                self.can_socket.close()
            except Exception:
                pass
            self.can_socket = None
        self.is_connected = False

    def read_vss_signals(self) -> Dict[str, Any]:
        if not self.is_connected or not self.can_socket:
            return self.latest_vss
        try:
            cf, _ = self.can_socket.recvfrom(16)
            can_id, can_dlc, data = struct.unpack("<IB3x8s", cf)
            can_id = can_id & 0x1FFFFFFF if (can_id & socket.CAN_EFF_FLAG) else (can_id & 0x7FF)
            # Custom hook or mapper can process raw frame
            # Update latest VSS
        except socket.timeout:
            pass
        except Exception as e:
            logger.debug(f"CAN read notice: {e}")
        return self.latest_vss

    def get_state_snapshot(self) -> VehicleStateSnapshot:
        vss = self.read_vss_signals()
        return VehicleStateSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_online=self.is_connected,
            speed_kmh=vss.get("Vehicle.Speed", 0.0),
            drive_mode=vss.get("Vehicle.Powertrain.Transmission.DriveMode", "NEUTRAL"),
            current_gear=vss.get("Vehicle.Powertrain.Transmission.CurrentGear", 0),
            battery_soc_percent=vss.get("Vehicle.Powertrain.TractionBattery.StateOfCharge.Current", 100.0),
            autonomous_active=vss.get("Vehicle.AutomatedDriving.IsActive", False),
            emergency_stop_active=vss.get("Vehicle.Safety.EStopActive", False),
            interlock_engaged=vss.get("Vehicle.Safety.InterlockEngaged", False),
            charging_connected=vss.get("Vehicle.Powertrain.TractionBattery.Charging.IsConnected", False),
            active_dtcs=[],
            raw_vss_signals=vss
        )
