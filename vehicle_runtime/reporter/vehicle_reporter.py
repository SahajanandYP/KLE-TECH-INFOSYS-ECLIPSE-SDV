"""
Vehicle Details & Heartbeat Reporter
Periodically gathers local hardware specs, software inventory, and live VSS state snapshot,
and posts them to the Central Jetson Registry over HTTP / REST.
"""

import time
import json
import urllib.request
import logging
from typing import Optional, Dict, Any

from vehicle_adapters.base.adapter_interface import (
    VehicleProfile,
    SoftwareInventory,
    BaseVehicleAdapter
)
from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker

logger = logging.getLogger("VehicleReporter")

class VehicleReporter:
    def __init__(
        self,
        central_server_url: str,
        profile: VehicleProfile,
        inventory: SoftwareInventory,
        adapter: BaseVehicleAdapter,
        broker: InMemoryVssBroker,
        heartbeat_interval_s: float = 2.0
    ):
        self.central_server_url = central_server_url.rstrip("/")
        self.profile = profile
        self.inventory = inventory
        self.adapter = adapter
        self.broker = broker
        self.heartbeat_interval_s = heartbeat_interval_s
        self.is_running = False

    def register_to_central(self) -> bool:
        url = f"{self.central_server_url}/api/v1/vehicles/register"
        payload = {
            "vehicle_id": self.profile.vehicle_id,
            "name": self.profile.name,
            "model": self.profile.model,
            "vehicle_type": self.profile.vehicle_type,
            "manufacturer": self.profile.manufacturer,
            "network_endpoint": f"http://localhost:5000",
            "hardware_profile": self.profile.to_dict(),
            "software_inventory": self.inventory.to_dict()
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Successfully registered with Central Registry at {self.central_server_url}")
                    return True
        except Exception as e:
            logger.warning(f"Registration to central server ({url}) failed: {e}")
        return False

    def send_heartbeat(self) -> bool:
        url = f"{self.central_server_url}/api/v1/vehicles/{self.profile.vehicle_id}/heartbeat"
        snapshot = self.adapter.get_state_snapshot()
        payload = {
            "current_state_snapshot": snapshot.to_dict(),
            "software_inventory": self.inventory.to_dict(),
            "active_dtcs": snapshot.active_dtcs
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    logger.debug(f"Heartbeat ACK from Central: {data.get('server_time')}")
                    return True
        except Exception as e:
            logger.debug(f"Heartbeat dispatch failed: {e}")
        return False

    def run_loop(self, max_iterations: Optional[int] = None):
        self.is_running = True
        self.register_to_central()

        count = 0
        while self.is_running:
            # Sync adapter signals to broker
            vss_signals = self.adapter.read_vss_signals()
            self.broker.update_bulk(vss_signals)

            # Send heartbeat snapshot to Central Registry
            self.send_heartbeat()

            count += 1
            if max_iterations and count >= max_iterations:
                break
            time.sleep(self.heartbeat_interval_s)

    def stop(self):
        self.is_running = False
