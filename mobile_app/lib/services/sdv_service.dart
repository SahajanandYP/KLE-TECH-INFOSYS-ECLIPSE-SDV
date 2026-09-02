import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;

class SDVVehicleService {
  String baseUrl;
  final String authToken;
  Timer? _pollingTimer;

  SDVVehicleService({
    this.baseUrl = "http://192.168.1.105:5000",
    this.authToken = "SDV_SECURE_TOKEN_2026",
  });

  Future<Map<String, dynamic>?> fetchLiveTelemetry() async {
    try {
      final res = await http.get(Uri.parse("$baseUrl/api/telemetry")).timeout(const Duration(seconds: 2));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (_) {}
    return null;
  }

  Future<bool> setLockState(bool lock) async {
    final action = lock ? "LOCK" : "UNLOCK";
    try {
      final res = await http.post(
        Uri.parse("$baseUrl/api/companion/command"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"token": authToken, "action": action}),
      ).timeout(const Duration(seconds: 3));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> fetchDiagnostics() async {
    try {
      final res = await http.get(Uri.parse("$baseUrl/api/diagnostics/sovd")).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (_) {}
    return null;
  }

  Future<bool> triggerOTAUpdate(String targetVersion) async {
    try {
      final res = await http.post(
        Uri.parse("$baseUrl/api/ota/trigger"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"target_version": targetVersion, "health_check_pass": true}),
      ).timeout(const Duration(seconds: 5));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
