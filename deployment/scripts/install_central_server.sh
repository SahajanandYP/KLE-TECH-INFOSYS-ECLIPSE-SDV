#!/usr/bin/env bash
# One-Line Central SDV Server Setup for NVIDIA Jetson AGX Orin & x86_64 Servers
set -e

PORT=${1:-8080}
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== Starting SDV Central Server on $(uname -m) (Port $PORT) ==="
mkdir -p "$DIR/central_server/registry"

nohup python3 "$DIR/central_server/server.py" "$PORT" > /tmp/central_server.log 2>&1 &
PID=$!
echo "Central Server launched with PID: $PID"

sleep 1
curl -s "http://localhost:$PORT/api/v1/health" | grep "HEALTHY" && echo "Central Server is UP and HEALTHY at http://localhost:$PORT"
