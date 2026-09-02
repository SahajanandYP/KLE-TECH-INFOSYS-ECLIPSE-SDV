"""
End-to-End System Integration Test
Tests complete distributed workflow:
1. Starts Central Registry HTTP Server on localhost:8899
2. Starts Vehicle Node with Mock Simulator & Reporter
3. Sends registration and multiple heartbeats
4. Queries Central Registry REST & OpenSOVD API
5. Asserts correct data synchronization and state persistence
"""

import unittest
import threading
import time
import urllib.request
import json
import sys
import os
from http.server import HTTPServer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from central_server.registry.registry_service import CentralVehicleRegistry
from central_server.registry.api import RegistryHttpHandler
from vehicle_adapters.base.adapter_interface import VehicleProfile, SoftwareInventory
from vehicle_adapters.mock_simulator.mock_adapter import MockVehicleAdapter
from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker
from vehicle_runtime.reporter.vehicle_reporter import VehicleReporter

class TestE2EPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8899
        cls.storage_file = "/tmp/e2e_vehicles.json"
        if os.path.exists(cls.storage_file):
            os.remove(cls.storage_file)

        cls.registry = CentralVehicleRegistry(storage_path=cls.storage_file)
        RegistryHttpHandler.registry = cls.registry

        cls.httpd = HTTPServer(("127.0.0.1", cls.port), RegistryHttpHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        if os.path.exists(cls.storage_file):
            os.remove(cls.storage_file)

    def test_e2e_vehicle_reporting_flow(self):
        central_url = f"http://127.0.0.1:{self.port}"
        profile = VehicleProfile(
            vehicle_id="e2e-vehicle-99",
            name="E2E Validation Node",
            model="SDV-Enterprise-X",
            vehicle_type="Electric Fleet",
            manufacturer="Eclipse SDV",
            max_speed_kmh=50.0,
            battery_capacity_kwh=8.0,
            communication_bus="Simulation"
        )
        inventory = SoftwareInventory(
            sdv_platform_version="v2.0.0",
            adapter_name="mock-adapter",
            adapter_version="v1.0.0",
            kuksa_broker_version="v0.4.1",
            os_kernel="5.15-tegra",
            cpu_arch="aarch64",
            active_workloads=["kuksa", "reporter"]
        )

        broker = InMemoryVssBroker()
        adapter = MockVehicleAdapter(profile)
        adapter.connect()

        reporter = VehicleReporter(
            central_server_url=central_url,
            profile=profile,
            inventory=inventory,
            adapter=adapter,
            broker=broker,
            heartbeat_interval_s=0.2
        )

        # Run 3 iterations
        reporter.run_loop(max_iterations=3)

        # Query Central Registry API
        url = f"{central_url}/api/v1/vehicles/e2e-vehicle-99"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))

        # Verify registration & live state snapshot
        self.assertEqual(data["vehicle_id"], "e2e-vehicle-99")
        self.assertEqual(data["status"], "ONLINE")
        self.assertEqual(data["model"], "SDV-Enterprise-X")
        self.assertEqual(data["software_inventory"]["sdv_platform_version"], "v2.0.0")
        self.assertIn("battery_soc_percent", data["current_state_snapshot"])
        self.assertIn("Vehicle.Speed", data["current_state_snapshot"]["raw_vss_signals"])

        # Query OpenSOVD diagnostics endpoint
        sovd_url = f"{central_url}/api/v1/vehicles/e2e-vehicle-99/diagnostics"
        with urllib.request.urlopen(sovd_url, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            sovd_data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(sovd_data["opensovd_version"], "1.0.0")
            self.assertIn("interlocks", sovd_data)

        adapter.disconnect()

if __name__ == "__main__":
    unittest.main()
