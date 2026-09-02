import 'package:flutter/material.dart';
import 'dart:async';
import 'services/sdv_service.dart';

void main() {
  runApp(const SDVCompanionApp());
}

class SDVCompanionApp extends StatelessWidget {
  const SDVCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Eclipse SDV Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F141C),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00B4D8),
          secondary: Color(0xFF00E676),
          surface: Color(0xFF18202F),
        ),
      ),
      home: const CompanionHomeScreen(),
    );
  }
}

class CompanionHomeScreen extends StatefulWidget {
  const CompanionHomeScreen({super.key});

  @override
  State<CompanionHomeScreen> createState() => _CompanionHomeScreenState();
}

class _CompanionHomeScreenState extends State<CompanionHomeScreen> {
  final SDVVehicleService _sdvService = SDVVehicleService();
  bool _isLocked = true;
  bool _isLoading = false;
  double _speed = 0.0;
  double _battery = 88.0;
  String _dbwStatus = "ACTIVE";
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startTelemetryLoop();
  }

  void _startTelemetryLoop() {
    _timer = Timer.periodic(const Duration(milliseconds: 1000), (_) async {
      final data = await _sdvService.fetchLiveTelemetry();
      if (data != null && mounted) {
        setState(() {
          _speed = (data['speed_kmh'] ?? 0.0).toDouble();
          _battery = (data['battery_soc_percent'] ?? 88.0).toDouble();
          _dbwStatus = (data['dbw_active'] == true) ? "ACTIVE" : "MANUAL";
        });
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _toggleLock() async {
    setState(() => _isLoading = true);
    final newState = !_isLocked;
    final success = await _sdvService.setLockState(newState);
    if (mounted) {
      setState(() {
        _isLoading = false;
        if (success) _isLocked = newState;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isLocked ? "Vehicle Locked Securely" : "Vehicle Unlocked & Ready"),
          backgroundColor: _isLocked ? Colors.redAccent : Colors.green,
          duration: const Duration(seconds: 1),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text("Eclipse SDV Companion", style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.wifi_tethering, color: Color(0xFF00E676)),
            onPressed: () {},
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Vehicle Hero Card
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFF18202F),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFF2A364F)),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text("Autonomous Skateboard", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                          SizedBox(height: 4),
                          Text("Target APM-V1 • Connected", style: TextStyle(fontSize: 13, color: Color(0xFF8D99AE))),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF00E676).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text("DBW $_dbwStatus", style: const TextStyle(color: Color(0xFF00E676), fontWeight: FontWeight.bold, fontSize: 12)),
                      )
                    ],
                  ),
                  const SizedBox(height: 30),
                  // Lock/Unlock Big Interactive Action Button
                  GestureDetector(
                    onTap: _isLoading ? null : _toggleLock,
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      width: 140,
                      height: 140,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isLocked ? const Color(0xFF2B1B22) : const Color(0xFF132B25),
                        border: Border.all(
                          color: _isLocked ? const Color(0xFFFF3366) : const Color(0xFF00E676),
                          width: 4,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: (_isLocked ? const Color(0xFFFF3366) : const Color(0xFF00E676)).withOpacity(0.3),
                            blurRadius: 20,
                            spreadRadius: 2,
                          )
                        ],
                      ),
                      child: Center(
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : Icon(
                                _isLocked ? Icons.lock : Icons.lock_open,
                                size: 54,
                                color: _isLocked ? const Color(0xFFFF3366) : const Color(0xFF00E676),
                              ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(_isLocked ? "TAP TO UNLOCK" : "TAP TO LOCK", style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.5, fontSize: 13, color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Live Telemetry Grid
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: const Color(0xFF18202F),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF2A364F)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("SPEED", style: TextStyle(color: Color(0xFF8D99AE), fontSize: 12, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text("${_speed.toStringAsFixed(1)}", style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
                        const Text("km/h", style: TextStyle(color: Color(0xFF00B4D8), fontSize: 12)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: const Color(0xFF18202F),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF2A364F)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("BATTERY SoC", style: TextStyle(color: Color(0xFF8D99AE), fontSize: 12, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text("${_battery.toStringAsFixed(0)}%", style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
                        const Text("5.2 kWh LiFePO4", style: TextStyle(color: Color(0xFF00E676), fontSize: 12)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
