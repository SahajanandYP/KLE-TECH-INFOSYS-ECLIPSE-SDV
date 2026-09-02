"""
Unit Tests for Mobile Companion SDK and Native Cluster
"""

import unittest
import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from vehicle_runtime.vehicle_stack import VehicleStack
from mobile_bridge.mobile_client_sdk import MobileCompanionClient

class TestMobileAndCluster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = VehicleStack(config_path="config/vss_mapping.yaml")
        cls.port = 5099
        cls.server_thread = threading.Thread(target=cls.stack.start, kwargs={"port": cls.port}, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    def test_mobile_companion_unlock_and_lock(self):
        client = MobileCompanionClient(endpoint_url=f"http://127.0.0.1:{self.port}", auth_token="SDV_SECURE_TOKEN_2026")
        
        # 1. Unlock
        success, msg = client.unlock_vehicle()
        self.assertTrue(success)
        self.assertIn("UNLOCKED", msg)

        # 2. Lock
        success, msg = client.lock_vehicle()
        self.assertTrue(success)
        self.assertIn("LOCKED", msg)

        # 3. Telemetry query from phone
        telemetry = client.get_live_telemetry()
        self.assertIsNotNone(telemetry)
        self.assertIn("speed_kmh", telemetry)
        self.assertIn("battery_soc_percent", telemetry)

        # 4. OpenSOVD query from phone
        sovd = client.get_opensovd_diagnostics()
        self.assertIsNotNone(sovd)
        self.assertEqual(sovd["protocol"], "ISO_17978_OpenSOVD")

    def test_invalid_token(self):
        client = MobileCompanionClient(endpoint_url=f"http://127.0.0.1:{self.port}", auth_token="WRONG_TOKEN")
        success, msg = client.unlock_vehicle()
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
