# Generalized Eclipse SDV Platform Architecture

## Core Architectural Principle
"Develop once. Configure per vehicle. Deploy across compatible edge compute platforms."

---

## 1. System Topology

```
+========================================================================================+
|                     CENTRAL SERVER & DEV HOST (NVIDIA Jetson AGX Orin)                 |
|                                                                                        |
|  - Central Vehicle Registry (REST & OpenSOVD APIs at port 8080)                        |
|  - Fleet Inventory (Hardware specs, software versions, online/offline status)          |
|  - Live VSS Snapshot Store (No high-rate time-series logs)                             |
|  - Central OTA Distribution & Artifact Server                                          |
+===========================================|============================================+
                                            |
                                            | HTTP REST / OpenSOVD / Zenoh (Heartbeat & Status)
                                            v
+========================================================================================+
|                     SYSTEM-DEPENDENT VEHICLE RUNTIME (Onboard / Remote Node)           |
|                                                                                        |
|  +----------------------------------------------------------------------------------+  |
|  | Vehicle Applications (Eclipse Velocitas Telemetry & Monitor)                      |  |
|  +----------------------------------------------------------------------------------+  |
|                                           |                                            |
|                                           v                                            |
|  +----------------------------------------------------------------------------------+  |
|  | Vehicle Data Layer (In-Memory / Eclipse KUKSA Databroker - COVESA VSS Tree)      |  |
|  +----------------------------------------------------------------------------------+  |
|                                           |                                            |
|                                           v                                            |
|  +----------------------------------------------------------------------------------+  |
|  | Vehicle Integration Boundary (Pluggable BaseVehicleAdapter Interface)            |  |
|  +----------------------------------------------------------------------------------+  |
|                                           |                                            |
|             +-----------------------------+-----------------------------+              |
|             |                                                           |              |
|             v                                                           v              |
|     [ Generic CAN Adapter ]                                   [ Mock Simulator ]       |
|     (SocketCAN 500k / CAN-FD)                                 (Physics Engine)         |
+========================================================================================+
```

---

## 2. Directory Structure

- `central_server/`: Central Vehicle Registry, OpenSOVD diagnostics API, and OTA manager.
- `vehicle_adapters/`: Base adapter interface, signal transformation engine, generic CAN, and mock simulator.
- `vehicle_runtime/`: Portable onboard daemon, KUKSA in-memory databroker, and vehicle reporter.
- `applications/`: Portable Eclipse Velocitas vehicle applications (Telemetry and Safety Monitor).
- `deployment/`: Multi-arch Dockerfiles, Compose manifests, Ankaios manifests, and one-line setup scripts.
- `tests/`: Automated unit and end-to-end integration tests.
- `docs/`: Comprehensive architecture, API, and platform guides.
