"""
Central Vehicle Registry Data Models
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

@dataclass
class VehicleRecord:
    vehicle_id: str
    name: str
    model: str
    vehicle_type: str
    manufacturer: str
    status: str # "ONLINE", "OFFLINE", "DEGRADED"
    first_registered: str
    last_seen: str
    network_endpoint: str
    hardware_profile: Dict[str, Any]
    software_inventory: Dict[str, Any]
    current_state_snapshot: Dict[str, Any]
    active_dtcs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VehicleRecord':
        return cls(**data)
