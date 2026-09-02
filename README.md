# Reusable Software Defined Vehicle (SDV) Platform

A reusable, hardware-agnostic **Software Defined Vehicle (SDV)** platform hosted on the **NVIDIA Jetson AGX Orin** (ARM64) as the central server and development host.

---

## Key Features

- **Central Fleet Details Registry**: Lightweight vehicle inventory and live state snapshot store (REST + OpenSOVD).
- **System-Dependent Vehicle Runtime**: Portable vehicle stack running on any target vehicle or remote developer machine.
- **Pluggable Vehicle Adapters**: Clean `BaseVehicleAdapter` abstraction for SocketCAN, ROS 2, SOME/IP, or Simulation.
- **COVESA VSS Data Layer**: Standard in-memory signal broker (`Vehicle.Speed`, `Vehicle.Powertrain.*`, etc.).
- **Multi-Architecture**: Native support for `linux/arm64` and `linux/amd64`.
- **Zero Heavy Dependencies**: Core platform runs on standard Python 3.10+ with optional containerization via Docker / Ankaios.

---

## Quick Start

### 1. Run Central Server (on Jetson / Server)
```bash
./deployment/scripts/install_central_server.sh
```
Check health:
```bash
curl http://localhost:8080/api/v1/health
```

### 2. Run Vehicle Node (on Vehicle / Remote Node)
```bash
./deployment/scripts/install_vehicle_node.sh http://localhost:8080 vehicle-01 mock
```

### 3. Query Central Fleet Registry
```bash
curl http://localhost:8080/api/v1/vehicles
curl http://localhost:8080/api/v1/vehicles/vehicle-01
curl http://localhost:8080/api/v1/vehicles/vehicle-01/diagnostics
```

### 4. Run Automated Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
