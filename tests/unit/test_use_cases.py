"""
Test Suite for the 5 Eclipse SDV Presentation Use Cases
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from vehicle_runtime.databroker.in_memory_broker import InMemoryVssBroker
from applications.companion_app import CompanionLockApp
from applications.telemetry_dashboard_app import TelemetryDashboardApp
from applications.opensovd_diagnostics_app import OpenSOVDDiagnosticsApp
from applications.ota_manager_app import OtaManagerApp
from applications.emergency_braking_app import EmergencyBrakingApp

class TestEclipseSdvUseCases(unittest.TestCase):
    def setUp(self):
        self.broker = InMemoryVssBroker()

    def test_use_case_1_companion_lock_unlock(self):
        app = CompanionLockApp(self.broker)
        
        # Test invalid token
        success, msg, _ = app.execute_command("INVALID_TOKEN", "UNLOCK")
        self.assertFalse(success)

        # Test valid unlock
        success, msg, data = app.execute_command("SDV_SECURE_TOKEN_2026", "UNLOCK")
        self.assertTrue(success)
        self.assertFalse(data["is_locked"])
        self.assertTrue(data["door_open"])
        self.assertEqual(self.broker.get_signal("Vehicle.Cabin.Door.Row1.Left.IsLocked"), False)

        # Test valid lock
        success, msg, data = app.execute_command("SDV_SECURE_TOKEN_2026", "LOCK")
        self.assertTrue(success)
        self.assertTrue(data["is_locked"])
        self.assertEqual(self.broker.get_signal("Vehicle.Cabin.Door.Row1.Left.IsLocked"), True)

    def test_use_case_2_telemetry_dashboard(self):
        app = TelemetryDashboardApp(self.broker)
        self.broker.set_signal("Vehicle.Speed", 28.5)
        self.broker.set_signal("Vehicle.Powertrain.TractionBattery.StateOfCharge.Current", 82.0)
        self.broker.set_signal("Vehicle.Chassis.SteeringWheel.Angle", -12.4)
        self.broker.set_signal("Vehicle.AutomatedDriving.IsActive", True)

        telemetry = app.get_dashboard_telemetry()
        self.assertEqual(telemetry["speed_kmh"], 28.5)
        self.assertEqual(telemetry["battery_soc_percent"], 82.0)
        self.assertEqual(telemetry["steering_angle_deg"], -12.4)
        self.assertTrue(telemetry["dbw_active"])
        self.assertEqual(telemetry["ecu_health"], "OPTIMAL")

    def test_use_case_3_opensovd_remote_diagnostics(self):
        software_inv = {"sdv_version": "v1.1.0", "kernel": "5.15-tegra"}
        app = OpenSOVDDiagnosticsApp(self.broker, software_inv)
        
        # Inject DTC fault
        app.inject_dtc("DTC_U0100_LOST_COMM_ENGINE")
        self.broker.set_signal("Vehicle.Safety.EStopActive", True)

        diag = app.get_sovd_diagnostics()
        self.assertEqual(diag["protocol"], "ISO_17978_OpenSOVD")
        self.assertIn("DTC_U0100_LOST_COMM_ENGINE", diag["active_faults_dtc"])
        self.assertTrue(diag["safety_interlocks"]["estop_tripped"])

    def test_use_case_4_ota_and_automated_rollback(self):
        app = OtaManagerApp(current_version="v1.1.0")

        # 1. Successful upgrade
        success, msg = app.apply_ota_update("v1.2.0", simulate_post_install_health_pass=True)
        self.assertTrue(success)
        self.assertEqual(app.current_version, "v1.2.0")
        self.assertEqual(app.update_state, "VERIFIED")

        # 2. Upgrade with failed health check -> Automated rollback
        success, msg = app.apply_ota_update("v1.3.0-buggy", simulate_post_install_health_pass=False)
        self.assertFalse(success)
        self.assertEqual(app.current_version, "v1.2.0") # Rolled back to previous stable
        self.assertEqual(app.update_state, "ROLLED_BACK")

    def test_use_case_5_ai_assisted_emergency_braking(self):
        app = EmergencyBrakingApp(self.broker, brake_distance_threshold_m=2.0)
        self.broker.set_signal("Vehicle.Speed", 30.0) # Traveling at 30 km/h

        # Obstacle far away (10m) -> No brake
        triggered, msg = app.process_obstacle_telemetry(distance_meters=10.0)
        self.assertFalse(triggered)
        self.assertEqual(self.broker.get_signal("Vehicle.Speed"), 30.0)

        # Obstacle close (1.2m) -> Automatic Emergency Braking
        triggered, msg = app.process_obstacle_telemetry(distance_meters=1.2)
        self.assertTrue(triggered)
        self.assertEqual(self.broker.get_signal("Vehicle.Speed"), 0.0)
        self.assertEqual(self.broker.get_signal("Vehicle.Chassis.Brake.PedalPosition"), 100.0)
        self.assertTrue(self.broker.get_signal("Vehicle.Safety.Braking.LLCStop"))

if __name__ == "__main__":
    unittest.main()
