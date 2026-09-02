import unittest
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from central_server.registry.registry_service import CentralVehicleRegistry

class TestCentralRegistry(unittest.TestCase):
    def setUp(self):
        self.test_storage = "/tmp/test_vehicles_registry.json"
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)
        self.registry = CentralVehicleRegistry(storage_path=self.test_storage)

    def tearDown(self):
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)

    def test_register_and_heartbeat(self):
        rec = self.registry.register_vehicle(
            vehicle_id="vehicle-bangalore-01",
            name="Bangalore Test Node",
            model="ThinkEdge-SE50",
            vehicle_type="Autonomous Skateboard",
            manufacturer="SDV Lab",
            network_endpoint="http://10.0.0.50:5000",
            hardware_profile={"max_speed_kmh": 40.0},
            software_inventory={"sdv_version": "v1.0.0"}
        )
        self.assertEqual(rec.vehicle_id, "vehicle-bangalore-01")
        self.assertEqual(rec.status, "ONLINE")

        # Heartbeat update
        updated = self.registry.record_heartbeat(
            vehicle_id="vehicle-bangalore-01",
            state_snapshot={"speed_kmh": 22.5, "battery_soc_percent": 84.0}
        )
        self.assertEqual(updated.current_state_snapshot["speed_kmh"], 22.5)

    def test_liveness_timeout(self):
        self.registry.register_vehicle(
            vehicle_id="vehicle-timeout",
            name="Timeout Node",
            model="Generic",
            vehicle_type="EV",
            manufacturer="SDV",
            network_endpoint="",
            hardware_profile={},
            software_inventory={}
        )
        # Force old last_seen
        self.registry.vehicles["vehicle-timeout"].last_seen = "2020-01-01T00:00:00+00:00"
        self.registry.check_liveness(timeout_seconds=5.0)
        self.assertEqual(self.registry.get_vehicle("vehicle-timeout").status, "OFFLINE")

if __name__ == "__main__":
    unittest.main()
