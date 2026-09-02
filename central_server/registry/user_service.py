"""
Central User Profile & Fleet Permission Service
Manages driver profiles, digital keys, and vehicle ownership.
"""

import json
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

@dataclass
class UserProfile:
    user_id: str
    full_name: str
    email: str
    role: str # "FLEET_MANAGER", "DRIVER", "TECHNICIAN"
    assigned_vehicle_ids: List[str] = field(default_factory=list)
    digital_key_token: str = "SDV_SECURE_TOKEN_2026"
    preferences: Dict[str, Any] = field(default_factory=lambda: {
        "max_speed_limit_kmh": 60.0,
        "climate_temp_c": 22.0,
        "drive_profile": "ECO"
    })
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CentralUserService:
    def __init__(self, storage_path: str = "central_server/registry/users.json"):
        self.storage_path = storage_path
        self.users: Dict[str, UserProfile] = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for uid, udata in data.items():
                        self.users[uid] = UserProfile(**udata)
            except Exception:
                self.users = {}
        if not self.users:
            # Seed default admin & driver profile
            self.create_user(
                user_id="user_admin_01",
                full_name="Lead SDV Engineer",
                email="admin@eclipse-sdv.org",
                role="FLEET_MANAGER",
                assigned_vehicles=["vehicle-apm-01", "generic-sdv-001"]
            )

    def save_to_disk(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({uid: u.to_dict() for uid, u in self.users.items()}, f, indent=2)

    def create_user(self, user_id: str, full_name: str, email: str, role: str, assigned_vehicles: List[str]) -> UserProfile:
        u = UserProfile(user_id=user_id, full_name=full_name, email=email, role=role, assigned_vehicle_ids=assigned_vehicles)
        self.users[user_id] = u
        self.save_to_disk()
        return u

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        return self.users.get(user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        return [u.to_dict() for u in self.users.values()]
