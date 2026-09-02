"""
Generalized Eclipse SDV Base Vehicle Adapter Interface
Defines the standard contract for any vehicle hardware/network adapter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

@dataclass
class VehicleProfile:
    vehicle_id: str
    name: str
    model: str
    vehicle_type: str
    manufacturer: str
    max_speed_kmh: float
    battery_capacity_kwh: float
    communication_bus: str # e.g. "SocketCAN", "Ethernet", "SOME/IP", "ROS2", "Simulation"
    extra_specs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SoftwareInventory:
    sdv_platform_version: str
    adapter_name: str
    adapter_version: str
    kuksa_broker_version: str
    os_kernel: str
    cpu_arch: str
    active_workloads: List[str] = field(default_factory=list)
    ota_target_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VehicleStateSnapshot:
    timestamp: str
    is_online: bool
    speed_kmh: float
    drive_mode: str # e.g. "FORWARD", "NEUTRAL", "REVERSE", "PARK"
    current_gear: int
    battery_soc_percent: float
    autonomous_active: bool
    emergency_stop_active: bool
    interlock_engaged: bool
    charging_connected: bool
    active_dtcs: List[str] = field(default_factory=list)
    raw_vss_signals: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BaseVehicleAdapter(ABC):
    """
    Abstract base class for all vehicle integrations (CAN, SOME/IP, ROS2, Mock).
    """

    def __init__(self, profile: VehicleProfile):
        self.profile = profile
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish physical or virtual connection to vehicle bus."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Safely close bus connection."""
        pass

    @abstractmethod
    def read_vss_signals(self) -> Dict[str, Any]:
        """
        Polls or extracts the latest normalized COVESA VSS signal dictionary.
        Must return standard VSS keys like:
        - Vehicle.Speed
        - Vehicle.Powertrain.TractionBattery.StateOfCharge.Current
        - Vehicle.Powertrain.Transmission.CurrentGear
        - Vehicle.Safety.EStopActive
        """
        pass

    @abstractmethod
    def get_state_snapshot(self) -> VehicleStateSnapshot:
        """Returns the high-level operational state snapshot."""
        pass
