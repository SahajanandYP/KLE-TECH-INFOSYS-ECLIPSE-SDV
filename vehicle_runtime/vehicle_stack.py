"""
Unified Vehicle SDV Stack Daemon
Runs on the target vehicle system.
1. Loads one-time operator VSS mapping from config/vss_mapping.yaml
2. Initializes KUKSA In-Memory Databroker
3. Launches all 5 Velocitas Use Case Applications
4. Connects to Jetson Central Registry & Exposes Local Endpoints
5. Autostarts on vehicle power-on via systemd
"""

import sys
import os
import yaml
import time
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker
from vehicle_adapters.base.adapter_interface import VehicleProfile, SoftwareInventory
from vehicle_adapters.mock_simulator.mock_adapter import MockVehicleAdapter
from vehicle_adapters.generic_can.generic_can_adapter import GenericCanAdapter
from vehicle_runtime.reporter.vehicle_reporter import VehicleReporter

from applications.companion_app import CompanionLockApp
from applications.telemetry_dashboard_app import TelemetryDashboardApp
from applications.opensovd_diagnostics_app import OpenSOVDDiagnosticsApp
from applications.ota_manager_app import OtaManagerApp
from applications.emergency_braking_app import EmergencyBrakingApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [VehicleStack] %(message)s")
logger = logging.getLogger("VehicleStack")

class VehicleStackApiHandler(BaseHTTPRequestHandler):
    stack = None

    def _send_json(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/api/telemetry" or path == "/":
            self._send_json(200, self.stack.telemetry_app.get_dashboard_telemetry())
        elif path == "/api/diagnostics/sovd":
            self._send_json(200, self.stack.diagnostics_app.get_sovd_diagnostics())
        elif path == "/api/ota/status":
            self._send_json(200, {"current_version": self.stack.ota_app.current_version, "state": self.stack.ota_app.update_state})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len).decode("utf-8")) if content_len > 0 else {}
        path = self.path.rstrip("/")

        if path == "/api/companion/command":
            token = body.get("token", "")
            action = body.get("action", "LOCK")
            success, msg, data = self.stack.companion_app.execute_command(token, action)
            self._send_json(200 if success else 403, {"success": success, "message": msg, "data": data})
        elif path == "/api/aeb/simulate_obstacle":
            dist = float(body.get("distance_meters", 10.0))
            triggered, msg = self.stack.aeb_app.process_obstacle_telemetry(dist)
            self._send_json(200, {"aeb_triggered": triggered, "message": msg})
        elif path == "/api/ota/trigger":
            target = body.get("target_version", "v1.2.0")
            health_pass = bool(body.get("health_check_pass", True))
            success, msg = self.stack.ota_app.apply_ota_update(target, health_pass)
            self._send_json(200, {"success": success, "message": msg, "version": self.stack.ota_app.current_version})
        else:
            self._send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        return

class VehicleStack:
    def __init__(self, config_path: str = "config/vss_mapping.yaml", central_url: str = "http://localhost:8080"):
        self.config_path = config_path
        self.central_url = central_url
        self.load_config()

        # 1. KUKSA VSS Broker
        self.broker = InMemoryVssBroker()

        # 2. Pluggable Adapter
        self.adapter = MockVehicleAdapter(self.profile) if self.bus_type == "Simulation" else GenericCanAdapter(self.profile, can_interface=self.can_if)
        self.adapter.connect()

        # 3. Velocitas Applications (All 5 Presentation Use Cases)
        self.companion_app = CompanionLockApp(self.broker)
        self.telemetry_app = TelemetryDashboardApp(self.broker)
        self.diagnostics_app = OpenSOVDDiagnosticsApp(self.broker, self.inventory.to_dict())
        self.ota_app = OtaManagerApp(current_version=self.inventory.sdv_platform_version)
        self.aeb_app = EmergencyBrakingApp(self.broker)

        # 4. Central Registry Reporter
        self.reporter = VehicleReporter(
            central_server_url=self.central_url,
            profile=self.profile,
            inventory=self.inventory,
            adapter=self.adapter,
            broker=self.broker,
            heartbeat_interval_s=2.0
        )

    def load_config(self):
        with open(self.config_path, "r") as f:
            cfg = yaml.safe_load(f)
        vp = cfg.get("vehicle_profile", {})
        self.bus_type = vp.get("bus_type", "Simulation")
        self.can_if = vp.get("interface", "can0")

        self.profile = VehicleProfile(
            vehicle_id=vp.get("id", "vehicle-01"),
            name=vp.get("name", "Vehicle Node"),
            model=vp.get("model", "APM-Skateboard"),
            vehicle_type="Autonomous Skateboard",
            manufacturer=vp.get("manufacturer", "VIRYA Mobility"),
            max_speed_kmh=54.0,
            battery_capacity_kwh=5.2,
            communication_bus=f"{self.bus_type} ({self.can_if})"
        )

        self.inventory = SoftwareInventory(
            sdv_platform_version="v1.1.0",
            adapter_name=f"{self.bus_type}-adapter",
            adapter_version="v1.0.0",
            kuksa_broker_version="v0.4.1",
            os_kernel=os.uname().release,
            cpu_arch=os.uname().machine,
            active_workloads=["kuksa-databroker", "companion-app", "telemetry-app", "opensovd-app", "aeb-app", "ota-manager"]
        )

    def start(self, port: int = 5000):
        VehicleStackApiHandler.stack = self
        server = HTTPServer(("0.0.0.0", port), VehicleStackApiHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        logger.info(f"Vehicle SDV Stack online! Local API on http://0.0.0.0:{port}")
        self.reporter.run_loop()

if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "config/vss_mapping.yaml"
    stack = VehicleStack(config_path=cfg_file)
    stack.start(port=5000)
