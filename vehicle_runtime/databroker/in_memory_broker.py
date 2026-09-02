"""
Lightweight In-Memory Eclipse KUKSA VSS Databroker
Provides standardized COVESA VSS signal storage, subscription callbacks, and thread-safe updates.
"""

import threading
import time
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timezone

class InMemoryVssBroker:
    def __init__(self):
        self._lock = threading.Lock()
        self._signals: Dict[str, Dict[str, Any]] = {}
        self._subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}
        self.init_standard_vss_tree()

    def init_standard_vss_tree(self):
        defaults = {
            "Vehicle.Speed": 0.0,
            "Vehicle.Powertrain.Transmission.CurrentGear": 0,
            "Vehicle.Powertrain.Transmission.DriveMode": "NEUTRAL",
            "Vehicle.Powertrain.Transmission.PerformanceMode": "NORMAL",
            "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": 100.0,
            "Vehicle.Powertrain.TractionBattery.Charging.IsConnected": False,
            "Vehicle.AutomatedDriving.IsActive": False,
            "Vehicle.Safety.EStopActive": False,
            "Vehicle.Safety.InterlockEngaged": False,
            "Vehicle.Safety.Braking.LLCStop": False,
            "Vehicle.CurrentLocation.Latitude": 0.0,
            "Vehicle.CurrentLocation.Longitude": 0.0
        }
        for path, val in defaults.items():
            self.set_signal(path, val)

    def set_signal(self, path: str, value: Any) -> None:
        with self._lock:
            now_iso = datetime.now(timezone.utc).isoformat()
            self._signals[path] = {
                "value": value,
                "timestamp": now_iso
            }
            subscribers = list(self._subscribers.get(path, [])) + list(self._subscribers.get("*", []))

        for cb in subscribers:
            try:
                cb(path, value)
            except Exception:
                pass

    def update_bulk(self, signals_dict: Dict[str, Any]) -> None:
        for path, val in signals_dict.items():
            self.set_signal(path, val)

    def get_signal(self, path: str) -> Optional[Any]:
        with self._lock:
            rec = self._signals.get(path)
            return rec["value"] if rec else None

    def get_all_signals(self) -> Dict[str, Any]:
        with self._lock:
            return {k: v["value"] for k, v in self._signals.items()}

    def subscribe(self, path: str, callback: Callable[[str, Any], None]) -> None:
        with self._lock:
            if path not in self._subscribers:
                self._subscribers[path] = []
            self._subscribers[path].append(callback)
