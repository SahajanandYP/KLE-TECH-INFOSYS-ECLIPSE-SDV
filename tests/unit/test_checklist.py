"""
Unit Tests for Checklist Enhancements (User Admin, VSS Catalog, BLE Proximity, Fault Isolation)
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from central_server.registry.user_service import CentralUserService
from vehicle_adapters.base.catalog_mapper import CatalogVssMapper
from mobile_bridge.ble_proximity_handler import BLEProximityHandler
from central_server.registry.fault_notifier import JetsonFaultNotifier

class TestChecklistItems(unittest.TestCase):
    def test_user_profile_management(self):
        srv = CentralUserService(storage_path="/tmp/test_users.json")
        user = srv.create_user(
            user_id="usr_test_99",
            full_name="Test Driver",
            email="driver@sdv.org",
            role="DRIVER",
            assigned_vehicles=["vehicle-apm-01"]
        )
        self.assertEqual(user.user_id, "usr_test_99")
        self.assertEqual(user.role, "DRIVER")
        self.assertIn("vehicle-apm-01", user.assigned_vehicle_ids)
        if os.path.exists("/tmp/test_users.json"):
            os.remove("/tmp/test_users.json")

    def test_standard_vss_catalog_mapping(self):
        mapper = CatalogVssMapper()
        # Test OBD2 Speed PID 0x0D
        res = mapper.map_standard_signal("OBD2_SPEED", 45.0)
        self.assertIsNotNone(res)
        path, val = res
        self.assertEqual(path, "Vehicle.Speed")
        self.assertEqual(val, 45.0)

        # Test J1939 Engine Temp
        res = mapper.map_standard_signal("J1939_ENGINE_TEMP", 125.0)
        self.assertIsNotNone(res)
        path, val = res
        self.assertEqual(path, "Vehicle.Powertrain.CombustionEngine.ECT")
        self.assertEqual(val, 85.0) # 125 - 40 = 85 C

    def test_ble_proximity_handler(self):
        unlocked = []
        handler = BLEProximityHandler(on_proximity_unlock=lambda: unlocked.append(True), rssi_threshold_dbm=-65)
        
        # Far away (-85 dBm) -> No unlock
        triggered = handler.simulate_ble_scan_step(rssi_dbm=-85)
        self.assertFalse(triggered)
        self.assertEqual(len(unlocked), 0)

        # Close proximity (-55 dBm) -> Unlock triggered
        triggered = handler.simulate_ble_scan_step(rssi_dbm=-55)
        self.assertTrue(triggered)
        self.assertEqual(len(unlocked), 1)

    def test_jetson_fault_isolation(self):
        notifier = JetsonFaultNotifier(log_path="/tmp/test_faults.log")
        notifier.notify_vehicle_fault("vehicle-apm-01", "Simulated CAN buffer overflow", "Traceback...")
        self.assertTrue(os.path.exists("/tmp/test_faults.log"))
        if os.path.exists("/tmp/test_faults.log"):
            os.remove("/tmp/test_faults.log")

if __name__ == "__main__":
    unittest.main()
