"""
Vehicle Node Main Daemon
Brings up Local VSS Databroker, Vehicle Adapter, and Vehicle Details Reporter.
"""

import sys
import os
import time
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from vehicle_adapters.base.adapter_interface import VehicleProfile, SoftwareInventory
from vehicle_adapters.mock_simulator.mock_adapter import MockVehicleAdapter
from vehicle_adapters.generic_can.generic_can_adapter import GenericCanAdapter
from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker
from vehicle_runtime.reporter.vehicle_reporter import VehicleReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [VehicleNode] %(message)s"
)
logger = logging.getLogger("VehicleNode")

def start_vehicle_node(
    vehicle_id: str = "generic-sdv-001",
    name: str = "SDV Prototype",
    central_url: str = "http://localhost:8080",
    adapter_type: str = "mock",
    can_interface: str = "vcan0"
):
    profile = VehicleProfile(
        vehicle_id=vehicle_id,
        name=name,
        model="Generic-SDV-2026",
        vehicle_type="Drive-by-Wire Electric",
        manufacturer="SDV Labs",
        max_speed_kmh=55.0,
        battery_capacity_kwh=6.0,
        communication_bus="Simulation" if adapter_type == "mock" else f"SocketCAN ({can_interface})"
    )

    inventory = SoftwareInventory(
        sdv_platform_version="v1.0.0",
        adapter_name=f"{adapter_type}-adapter",
        adapter_version="v1.0.0",
        kuksa_broker_version="v0.4.1",
        os_kernel=os.uname().release,
        cpu_arch=os.uname().machine,
        active_workloads=["kuksa-databroker", f"{adapter_type}-adapter", "vehicle-reporter"]
    )

    broker = InMemoryVssBroker()

    if adapter_type == "mock":
        adapter = MockVehicleAdapter(profile)
    else:
        adapter = GenericCanAdapter(profile, can_interface=can_interface)

    adapter.connect()

    reporter = VehicleReporter(
        central_server_url=central_url,
        profile=profile,
        inventory=inventory,
        adapter=adapter,
        broker=broker,
        heartbeat_interval_s=1.0
    )

    logger.info(f"Starting Vehicle Node for '{vehicle_id}' (Adapter: {adapter_type})...")
    try:
        reporter.run_loop()
    except KeyboardInterrupt:
        logger.info("Stopping Vehicle Node...")
        reporter.stop()
        adapter.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SDV Vehicle Node Daemon")
    parser.add_argument("--id", default="generic-sdv-001", help="Vehicle ID")
    parser.add_argument("--name", default="SDV Vehicle Node", help="Vehicle Name")
    parser.add_argument("--central-url", default="http://localhost:8080", help="Central Jetson Server URL")
    parser.add_argument("--adapter", choices=["mock", "can"], default="mock", help="Adapter type")
    parser.add_argument("--can-if", default="vcan0", help="CAN interface if using CAN adapter")
    args = parser.parse_args()

    start_vehicle_node(
        vehicle_id=args.id,
        name=args.name,
        central_url=args.central_url,
        adapter_type=args.adapter,
        can_interface=args.can_if
    )
