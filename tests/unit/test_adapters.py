import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from vehicle_adapters.base.adapter_interface import VehicleProfile, SoftwareInventory
from vehicle_adapters.base.signal_mapping import GenericSignalMapper, SignalMappingRule
from vehicle_adapters.mock_simulator.mock_adapter import MockVehicleAdapter
from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker

class TestGenericAdapters(unittest.TestCase):
    def test_mock_adapter_simulation(self):
        profile = VehicleProfile(
            vehicle_id="test-v-01",
            name="Test Vehicle",
            model="Sim-2026",
            vehicle_type="EV",
            manufacturer="SDV Lab",
            max_speed_kmh=60.0,
            battery_capacity_kwh=10.0,
            communication_bus="Simulation"
        )
        adapter = MockVehicleAdapter(profile)
        self.assertTrue(adapter.connect())

        snapshot = adapter.get_state_snapshot()
        self.assertTrue(snapshot.is_online)
        self.assertIn("Vehicle.Speed", snapshot.raw_vss_signals)
        self.assertIn("Vehicle.Powertrain.TractionBattery.StateOfCharge.Current", snapshot.raw_vss_signals)

    def test_signal_mapper_rules(self):
        mapper = GenericSignalMapper([
            SignalMappingRule("raw_speed_mps", "Vehicle.Speed", scale=3.6),
            SignalMappingRule("raw_gear", "Vehicle.Powertrain.Transmission.CurrentGear", value_map={0: 0, 1: 1, 2: -1})
        ])
        raw_telemetry = {"raw_speed_mps": 10.0, "raw_gear": 1}
        vss = mapper.map_to_vss(raw_telemetry)
        self.assertEqual(vss["Vehicle.Speed"], 36.0)
        self.assertEqual(vss["Vehicle.Powertrain.Transmission.CurrentGear"], 1)

    def test_in_memory_broker_subscriptions(self):
        broker = InMemoryVssBroker()
        received = []
        broker.subscribe("Vehicle.Speed", lambda path, val: received.append((path, val)))

        broker.set_signal("Vehicle.Speed", 25.4)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], ("Vehicle.Speed", 25.4))
        self.assertEqual(broker.get_signal("Vehicle.Speed"), 25.4)

if __name__ == "__main__":
    unittest.main()
