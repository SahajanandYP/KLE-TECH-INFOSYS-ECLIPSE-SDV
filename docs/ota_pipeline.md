# Generalized Over-The-Air (OTA) Pipeline

1. **Multi-Architecture OCI Packaging**: All vehicle runtime components and central server services are containerized for `linux/arm64` and `linux/amd64`.
2. **Workload Manifest Orchestration (Eclipse Ankaios + Kanto)**:
   - Vehicle workloads are declared in `deployment/ankaios/vehicle_state.yaml`.
   - Workloads update atomically with zero downtime.
3. **Rollback & Safety Guard**: Updates are applied only when vehicle safety criteria are met (`Vehicle.Speed == 0` and vehicle stationary).
