"""
Central Vehicle Registry REST & OpenSOVD API
Zero-dependency high performance HTTP API using Python standard library.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from .registry_service import CentralVehicleRegistry

logger = logging.getLogger("RegistryAPI")

class RegistryHttpHandler(BaseHTTPRequestHandler):
    registry: CentralVehicleRegistry = None

    def _send_json_response(self, status_code: int, data: Any):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")

        # Health Check
        if path == "/api/v1/health" or path == "":
            self._send_json_response(200, {
                "status": "HEALTHY",
                "service": "SDV Central Vehicle Registry",
                "vehicles_count": len(self.registry.vehicles)
            })
            return

        # List all vehicles
        if path == "/api/v1/vehicles":
            self.registry.check_liveness()
            self._send_json_response(200, {
                "count": len(self.registry.vehicles),
                "vehicles": self.registry.list_vehicles()
            })
            return

        # Single vehicle details: /api/v1/vehicles/{vehicle_id}
        if path.startswith("/api/v1/vehicles/"):
            vehicle_id = path.split("/api/v1/vehicles/")[1]
            if "/" in vehicle_id:
                # Sub-resource check, e.g. /diagnostics
                parts = vehicle_id.split("/")
                vid, subresource = parts[0], parts[1]
                v = self.registry.get_vehicle(vid)
                if not v:
                    self._send_json_response(404, {"error": f"Vehicle '{vid}' not found."})
                    return
                if subresource == "diagnostics":
                    self._send_json_response(200, {
                        "vehicle_id": vid,
                        "opensovd_version": "1.0.0",
                        "status": v.status,
                        "last_seen": v.last_seen,
                        "active_dtcs": v.active_dtcs,
                        "hardware_profile": v.hardware_profile,
                        "software_inventory": v.software_inventory,
                        "interlocks": {
                            "emergency_stop": v.current_state_snapshot.get("emergency_stop_active", False),
                            "interlock_engaged": v.current_state_snapshot.get("interlock_engaged", False),
                            "charging_connected": v.current_state_snapshot.get("charging_connected", False)
                        }
                    })
                    return
            else:
                v = self.registry.get_vehicle(vehicle_id)
                if v:
                    self._send_json_response(200, v.to_dict())
                else:
                    self._send_json_response(404, {"error": f"Vehicle '{vehicle_id}' not found."})
                return

        # Fallback 404
        self._send_json_response(404, {"error": "Endpoint not found."})

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            self._send_json_response(400, {"error": "Invalid JSON body."})
            return

        # Register vehicle: POST /api/v1/vehicles/register
        if path == "/api/v1/vehicles/register":
            required = ["vehicle_id", "name", "model"]
            if not all(k in payload for k in required):
                self._send_json_response(400, {"error": f"Missing required fields: {required}"})
                return
            
            record = self.registry.register_vehicle(
                vehicle_id=payload["vehicle_id"],
                name=payload.get("name", payload["vehicle_id"]),
                model=payload.get("model", "Generic-SDV"),
                vehicle_type=payload.get("vehicle_type", "Electric"),
                manufacturer=payload.get("manufacturer", "Generic"),
                network_endpoint=payload.get("network_endpoint", ""),
                hardware_profile=payload.get("hardware_profile", {}),
                software_inventory=payload.get("software_inventory", {})
            )
            self._send_json_response(201, {"status": "REGISTERED", "vehicle": record.to_dict()})
            return

        # Heartbeat: POST /api/v1/vehicles/{vehicle_id}/heartbeat
        if path.startswith("/api/v1/vehicles/") and path.endswith("/heartbeat"):
            vehicle_id = path.replace("/api/v1/vehicles/", "").replace("/heartbeat", "")
            state_snapshot = payload.get("current_state_snapshot", payload)
            software_inv = payload.get("software_inventory", None)
            dtcs = payload.get("active_dtcs", None)

            rec = self.registry.record_heartbeat(
                vehicle_id=vehicle_id,
                state_snapshot=state_snapshot,
                software_inventory=software_inv,
                dtcs=dtcs
            )
            self._send_json_response(200, {
                "status": "ACK",
                "vehicle_id": vehicle_id,
                "server_time": rec.last_seen,
                "ota_target": rec.software_inventory.get("ota_target_version", None)
            })
            return

        self._send_json_response(404, {"error": "Endpoint not found."})

    def log_message(self, format, *args):
        # Override to suppress default noisy stderr logs in test
        return
