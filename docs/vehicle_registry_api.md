# Central Vehicle Registry & OpenSOVD API Reference

Base URL: `http://<jetson-ip>:8080`

---

## Endpoints

### 1. Health Check
- **GET** `/api/v1/health`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "SDV Central Vehicle Registry",
  "vehicles_count": 2
}
```

### 2. List All Vehicles
- **GET** `/api/v1/vehicles`
- **Response**:
```json
{
  "count": 1,
  "vehicles": [
    {
      "vehicle_id": "remote-sdv-01",
      "name": "Vehicle remote-sdv-01",
      "status": "ONLINE",
      "last_seen": "2026-09-02T15:20:00Z"
    }
  ]
}
```

### 3. Get Vehicle Details & Live Snapshot
- **GET** `/api/v1/vehicles/{vehicle_id}`
- **Response**: Full `VehicleRecord` JSON containing `hardware_profile`, `software_inventory`, and `current_state_snapshot`.

### 4. Vehicle Registration
- **POST** `/api/v1/vehicles/register`
- **Body**:
```json
{
  "vehicle_id": "sdv-node-01",
  "name": "SDV Prototype",
  "model": "Generic-SDV",
  "vehicle_type": "Electric",
  "manufacturer": "SDV Lab",
  "hardware_profile": { "max_speed_kmh": 60.0 },
  "software_inventory": { "sdv_platform_version": "v1.0.0" }
}
```

### 5. Vehicle Heartbeat
- **POST** `/api/v1/vehicles/{vehicle_id}/heartbeat`
- **Body**:
```json
{
  "current_state_snapshot": {
    "speed_kmh": 24.5,
    "battery_soc_percent": 88.0,
    "drive_mode": "FORWARD"
  }
}
```

### 6. OpenSOVD Diagnostics
- **GET** `/api/v1/vehicles/{vehicle_id}/diagnostics`
- **Response**: Active DTCs, interlock states, software inventory.
