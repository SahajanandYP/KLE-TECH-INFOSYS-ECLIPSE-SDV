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
            
            # Mask out the 29-bit identifier properly (EFF flag is bit 31)
            is_extended = bool(can_id & 0x80000000)
            if is_extended:
                can_id = can_id & 0x1FFFFFFF
            else:
                can_id = can_id & 0x7FF
            
            # Match Proprietary B - General Status
            # The PDF manual says PGN: "0x1291 0109". This could be a full 29-bit ID (0x12910109) 
            # or a J1939 PGN (0x1291). We check all possibilities to be bulletproof.
            # Strict match for exactly 0x1291 or any J1939 with PGN 1291
            pgn = (can_id >> 8) & 0x3FFFF
            
            # Mask just the hex string to see if it literally ends in 1291 for weird cases
            hex_id_str = hex(can_id)
            
            if can_id == 0x1291 or can_id == 0x12910109 or pgn == 0x1291 or hex_id_str.endswith("1291"):
                # Avoid overwriting with blank multiplexed frames. If byte 0 is 0 and byte 5 is 0, ignore.
                if data[0] == 0x00 and data[5] == 0x00 and data[6] == 0x00:
                    pass
                else:
                    # B0 - Drive Mode (0x01=Forward, 0x03=Reverse, 0x00=Neutral)
                    d_mode = data[0]
                    if d_mode == 0x01:
                        self.latest_vss["Vehicle.Powertrain.Transmission.CurrentGear"] = 1
                        self.latest_vss["Vehicle.Powertrain.Transmission.DriveMode"] = "DRIVE"
                    elif d_mode == 0x03:
                        self.latest_vss["Vehicle.Powertrain.Transmission.CurrentGear"] = -1
                        self.latest_vss["Vehicle.Powertrain.Transmission.DriveMode"] = "REVERSE"
                    else:
                        self.latest_vss["Vehicle.Powertrain.Transmission.CurrentGear"] = 0
                        self.latest_vss["Vehicle.Powertrain.Transmission.DriveMode"] = "NEUTRAL"
                        
                    # B4 - Vehicle Status Flags
                    status_bits = data[4]
                    self.latest_vss["Vehicle.AutomatedDriving.IsActive"] = bool(status_bits & 0x01)
                    self.latest_vss["Vehicle.Safety.EStopActive"] = bool(status_bits & 0x10)
                    
                    # B5 - Battery Percentage
                    # Only update if it's non-zero or seems reasonable to avoid blank frames zeroing it
                    if data[5] != 0:
                        self.latest_vss["Vehicle.Powertrain.TractionBattery.StateOfCharge.Current"] = float(data[5])
                    
                    # B6-B7 - Vehicle Speed in mps (Speed * 0.01). Convert to km/h!
                    speed_raw = data[6] | (data[7] << 8)
                    speed_mps = speed_raw * 0.01
                    self.latest_vss["Vehicle.Speed"] = speed_mps * 3.6
                
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
