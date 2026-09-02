"""
Central Vehicle Registry Service
Maintains persistent store of all connected vehicles, hardware profiles, software versions, and live snapshots.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .models import VehicleRecord

logger = logging.getLogger("CentralVehicleRegistry")

class CentralVehicleRegistry:
    def __init__(self, storage_path: str = "central-server/registry/vehicles.json"):
        self.storage_path = storage_path
        self.vehicles: Dict[str, VehicleRecord] = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for vid, vdata in data.items():
                        self.vehicles[vid] = VehicleRecord.from_dict(vdata)
                logger.info(f"Loaded {len(self.vehicles)} vehicle records from {self.storage_path}")
            except Exception as e:
                logger.error(f"Error loading registry: {e}")
                self.vehicles = {}

    def save_to_disk(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                serializable = {vid: v.to_dict() for vid, v in self.vehicles.items()}
                json.dump(serializable, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving registry to disk: {e}")

    def register_vehicle(
        self,
        vehicle_id: str,
        name: str,
        model: str,
        vehicle_type: str,
        manufacturer: str,
        network_endpoint: str,
        hardware_profile: Dict[str, Any],
        software_inventory: Dict[str, Any]
    ) -> VehicleRecord:
        now_iso = datetime.now(timezone.utc).isoformat()
        if vehicle_id in self.vehicles:
            rec = self.vehicles[vehicle_id]
            rec.name = name
            rec.model = model
            rec.vehicle_type = vehicle_type
            rec.manufacturer = manufacturer
            rec.network_endpoint = network_endpoint
            rec.hardware_profile = hardware_profile
            rec.software_inventory = software_inventory
            rec.last_seen = now_iso
            rec.status = "ONLINE"
        else:
            rec = VehicleRecord(
                vehicle_id=vehicle_id,
                name=name,
                model=model,
                vehicle_type=vehicle_type,
                manufacturer=manufacturer,
                status="ONLINE",
                first_registered=now_iso,
                last_seen=now_iso,
                network_endpoint=network_endpoint,
                hardware_profile=hardware_profile,
                software_inventory=software_inventory,
                current_state_snapshot={},
                active_dtcs=[]
            )
            self.vehicles[vehicle_id] = rec
        
        self.save_to_disk()
        logger.info(f"Vehicle '{vehicle_id}' successfully registered/updated in Central Registry.")
        return rec

    def record_heartbeat(
        self,
        vehicle_id: str,
        state_snapshot: Dict[str, Any],
        software_inventory: Optional[Dict[str, Any]] = None,
        dtcs: Optional[List[str]] = None
    ) -> Optional[VehicleRecord]:
        now_iso = datetime.now(timezone.utc).isoformat()
        if vehicle_id not in self.vehicles:
            logger.warning(f"Received heartbeat from unregistered vehicle '{vehicle_id}'. Auto-registering basic profile.")
            self.register_vehicle(
                vehicle_id=vehicle_id,
                name=f"Vehicle-{vehicle_id}",
                model="Generic-SDV",
                vehicle_type="Unknown",
                manufacturer="Unknown",
                network_endpoint="unknown",
                hardware_profile={},
                software_inventory=software_inventory or {}
            )

        rec = self.vehicles[vehicle_id]
        rec.last_seen = now_iso
        rec.status = "ONLINE"
        rec.current_state_snapshot = state_snapshot
        if software_inventory:
            rec.software_inventory.update(software_inventory)
        if dtcs is not None:
            rec.active_dtcs = dtcs

        self.save_to_disk()
        return rec

    def get_vehicle(self, vehicle_id: str) -> Optional[VehicleRecord]:
        return self.vehicles.get(vehicle_id)

    def list_vehicles(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.vehicles.values()]

    def check_liveness(self, timeout_seconds: float = 30.0):
        """Marks vehicles whose heartbeat timed out as OFFLINE."""
        now = datetime.now(timezone.utc)
        changed = False
        for vid, v in self.vehicles.items():
            if v.status == "ONLINE":
                try:
                    last_seen_dt = datetime.fromisoformat(v.last_seen.replace("Z", "+00:00"))
                    if (now - last_seen_dt).total_seconds() > timeout_seconds:
                        v.status = "OFFLINE"
                        changed = True
                except Exception:
                    pass
        if changed:
            self.save_to_disk()
