"""
Central SDV Registry Server Executable
Runs on NVIDIA Jetson AGX Orin as the primary edge server.
"""

import sys
import os
import logging
from http.server import HTTPServer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from central_server.registry.registry_service import CentralVehicleRegistry
from central_server.registry.api import RegistryHttpHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [CentralServer] %(message)s"
)
logger = logging.getLogger("CentralServer")

def run_server(host: str = "0.0.0.0", port: int = 8080):
    registry = CentralVehicleRegistry(storage_path="central-server/registry/vehicles.json")
    RegistryHttpHandler.registry = registry

    server_address = (host, port)
    httpd = HTTPServer(server_address, RegistryHttpHandler)
    logger.info(f"Central SDV Registry Server running at http://{host}:{port}")
    logger.info(f"OpenSOVD & REST API Endpoints active at /api/v1/vehicles")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Central Registry Server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port=port)
