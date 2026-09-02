#!/usr/bin/env bash
# One-Line Vehicle Node Installer for Target Vehicles / Remote Nodes (e.g. Bangalore)
set -e

CENTRAL_URL=${1:-"http://localhost:8080"}
VEHICLE_ID=${2:-"remote-sdv-01"}
ADAPTER=${3:-"mock"} # "mock" or "can"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== Launching SDV Vehicle Node on $(uname -m) ==="
echo "Central Registry URL: $CENTRAL_URL"
echo "Vehicle ID: $VEHICLE_ID (Adapter: $ADAPTER)"

python3 "$DIR/vehicle_runtime/core/vehicle_daemon.py" \
    --id "$VEHICLE_ID" \
    --name "Vehicle $VEHICLE_ID" \
    --central-url "$CENTRAL_URL" \
    --adapter "$ADAPTER"
