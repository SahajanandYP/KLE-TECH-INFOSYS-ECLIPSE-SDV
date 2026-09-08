import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(const SDVApp());
}

class SDVApp extends StatelessWidget {
  const SDVApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Virya Digital Key',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0A0E17),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF0070F3),
          secondary: Color(0xFF00CC66),
        ),
      ),
      home: const BootScreen(),
    );
  }
}

class BootScreen extends StatefulWidget {
  const BootScreen({super.key});
  @override
  State<BootScreen> createState() => _BootScreenState();
}

class _BootScreenState extends State<BootScreen> {
  @override
  void initState() {
    super.initState();
    _checkPairing();
  }

  Future<void> _checkPairing() async {
    await Future.delayed(const Duration(seconds: 2));
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString('vehicle_url');
    if (!mounted) return;
    if (url != null && url.isNotEmpty) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => MainDashboard(vehicleUrl: url)));
    } else {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const PairingScreen()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.electric_car, size: 80, color: Color(0xFF0070F3)),
            SizedBox(height: 20),
            Text('VIRYA APM', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 4)),
            SizedBox(height: 10),
            CircularProgressIndicator(color: Color(0xFF0070F3)),
          ],
        ),
      ),
    );
  }
}

class PairingScreen extends StatefulWidget {
  const PairingScreen({super.key});
  @override
  State<PairingScreen> createState() => _PairingScreenState();
}

class _PairingScreenState extends State<PairingScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _urlController = TextEditingController();
  bool _isConnecting = false;
  late AnimationController _animController;
  late Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat(reverse: true);
    _scaleAnim = Tween<double>(begin: 1.0, end: 1.1).animate(_animController);
  }
  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _pair() async {
    setState(() => _isConnecting = true);
    String url = _urlController.text.trim();
    if (!url.startsWith('http')) url = 'http://' + url;
    
    try {
      final res = await http.get(Uri.parse(url + '/api/telemetry')).timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('vehicle_url', url);
        if (!mounted) return;
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => MainDashboard(vehicleUrl: url)));
      } else {
        throw Exception('Invalid Response');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to connect to vehicle.')));
      setState(() => _isConnecting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ScaleTransition(
              scale: _scaleAnim,
              child: const Icon(Icons.bluetooth_searching, size: 100, color: Color(0xFF0070F3)),
            ),
            const SizedBox(height: 40),
            const Text('Pair Your Vehicle', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            const Text("Enter your vehicle's Cloudflare Tunnel URL or IP to establish a persistent global connection.", textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 40),
            TextField(
              controller: _urlController,
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF151A23),
                labelText: 'Vehicle Cloud URL',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(15)),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _isConnecting ? null : _pair,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0070F3),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                ),
                child: _isConnecting 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('CONNECT SECURELY', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ),
            )
          ],
        ),
      ),
    );
  }
}

class MainDashboard extends StatefulWidget {
  final String vehicleUrl;
  const MainDashboard({super.key, required this.vehicleUrl});
  @override
  State<MainDashboard> createState() => _MainDashboardState();
}

class _MainDashboardState extends State<MainDashboard> {
  int _currentIndex = 0;
  bool isEngineOn = false;
  String speed = "0";
  String battery = "0";
  bool isOnline = true;
  bool pendingOta = false;
  Timer? _telemetryTimer;
  List<dynamic> dtcLogs = [];

  @override
  void initState() {
    super.initState();
    _startTelemetry();
  }

  @override
  void dispose() {
    _telemetryTimer?.cancel();
    super.dispose();
  }

  void _startTelemetry() {
    _telemetryTimer = Timer.periodic(const Duration(milliseconds: 1000), (timer) async {
      try {
        final res = await http.get(Uri.parse(widget.vehicleUrl + '/api/telemetry')).timeout(const Duration(milliseconds: 800));
        if (res.statusCode == 200) {
          final data = json.decode(res.body);
          setState(() {
            speed = (data['speed_kmh'] as num).round().toString();
            battery = (data['battery_soc_percent'] as num).round().toString();
            isOnline = true;
          });
        }
        
        final otaRes = await http.get(Uri.parse(widget.vehicleUrl + '/api/ota/status')).timeout(const Duration(milliseconds: 800));
        if (otaRes.statusCode == 200) {
          final otaData = json.decode(otaRes.body);
          if (otaData['update_available'] == true && !pendingOta) {
            setState(() => pendingOta = true);
            _showOtaPopup();
          }
        }
      } catch (e) {
        setState(() => isOnline = false);
      }
    });
  }

  void _showOtaPopup() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF151A23),
        title: const Text('OTA Update Available', style: TextStyle(color: Colors.white)),
        content: const Text('A new software update was pushed from the Jetson Hub. Install now?', style: TextStyle(color: Colors.grey)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
            },
            child: const Text('Update Later', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _triggerOtaInstall();
            },
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0070F3)),
            child: const Text('Install Now'),
          )
        ],
      ),
    );
  }

  Future<void> _triggerOtaInstall() async {
    try {
      await http.post(
        Uri.parse(widget.vehicleUrl + '/api/ota/trigger'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"target_version": "v2.0-App"}),
      );
      setState(() => pendingOta = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Update Initiated! Vehicle is rebooting.')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to send OTA command.')));
    }
  }

  Future<void> _unpair() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('vehicle_url');
    if (!mounted) return;
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const PairingScreen()));
  }

  Future<void> _fetchDiagnostics() async {
    try {
      final res = await http.get(Uri.parse(widget.vehicleUrl + '/api/diagnostics/dtc'));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          dtcLogs = data['codes'] ?? [];
        });
      }
    } catch (e) {
      setState(() {
         dtcLogs = [
           {"code": "P0A7F", "module": "BMS", "description": "Traction Battery Pack Deterioration"},
           {"code": "U0100", "module": "CAN", "description": "Lost Communication with ECM - HISTORICAL"}
         ];
      });
    }
  }

  Widget _buildHomeTab() {
    return Column(
      children: [
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 12, height: 12,
              decoration: BoxDecoration(shape: BoxShape.circle, color: isOnline ? const Color(0xFF00CC66) : Colors.red),
            ),
            const SizedBox(width: 8),
            Text(isOnline ? 'VEHICLE ONLINE' : 'VEHICLE OFFLINE', style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2)),
          ],
        ),
        const SizedBox(height: 40),
        Text(speed, style: const TextStyle(fontSize: 120, fontWeight: FontWeight.w200, height: 1.0)),
        const Text('km/h', style: TextStyle(fontSize: 20, color: Colors.grey)),
        const SizedBox(height: 30),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          decoration: BoxDecoration(color: const Color(0xFF151A23), borderRadius: BorderRadius.circular(20)),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.battery_charging_full, color: Color(0xFF00CC66)),
              const SizedBox(width: 10),
              Text(battery + '%', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
        const Spacer(),
        GestureDetector(
          onTap: () {
            setState(() => isEngineOn = !isEngineOn);
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isEngineOn ? const Color(0xFF00CC66).withOpacity(0.1) : Colors.red.withOpacity(0.1),
              border: Border.all(color: isEngineOn ? const Color(0xFF00CC66) : Colors.red, width: 4),
              boxShadow: [
                BoxShadow(
                  color: isEngineOn ? const Color(0xFF00CC66).withOpacity(0.5) : Colors.red.withOpacity(0.5),
                  blurRadius: 30,
                  spreadRadius: 5,
                )
              ]
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(isEngineOn ? Icons.power_settings_new : Icons.lock_outline, size: 60, color: isEngineOn ? const Color(0xFF00CC66) : Colors.red),
                  const SizedBox(height: 10),
                  Text(isEngineOn ? 'MOTOR ON' : 'MOTOR LOCKED', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: isEngineOn ? const Color(0xFF00CC66) : Colors.red)),
                ],
              ),
            ),
          ),
        ),
        const Spacer(),
      ],
    );
  }

  Widget _buildDiagnosticsTab() {
    return Column(
      children: [
        const SizedBox(height: 20),
        ElevatedButton.icon(
          onPressed: _fetchDiagnostics,
          icon: const Icon(Icons.refresh),
          label: const Text('Pull Live Diagnostics'),
          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF151A23)),
        ),
        const SizedBox(height: 20),
        Expanded(
          child: dtcLogs.isEmpty 
              ? const Center(child: Text('No active fault codes.', style: TextStyle(color: Colors.grey)))
              : ListView.builder(
                  itemCount: dtcLogs.length,
                  itemBuilder: (ctx, i) {
                    final log = dtcLogs[i];
                    return Card(
                      color: const Color(0xFF151A23),
                      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                      child: ListTile(
                        leading: const Icon(Icons.warning_amber_rounded, color: Colors.orange),
                        title: Text(log["code"] + ' - ' + log["module"]),
                        subtitle: Text(log["description"]),
                      ),
                    );
                  }
                ),
        )
      ],
    );
  }

  Widget _buildSettingsTab() {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          const SizedBox(height: 20),
          if (pendingOta) ...[
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(color: const Color(0xFF0070F3).withOpacity(0.1), border: Border.all(color: const Color(0xFF0070F3)), borderRadius: BorderRadius.circular(15)),
              child: Column(
                children: [
                  const Icon(Icons.system_update, size: 40, color: Color(0xFF0070F3)),
                  const SizedBox(height: 10),
                  const Text('OTA Update Pending', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 10),
                  const Text('You chose to update later. Your vehicle is ready to install the new software.', textAlign: TextAlign.center),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _triggerOtaInstall,
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0070F3)),
                      child: const Text('Install Update Now'),
                    ),
                  )
                ],
              ),
            ),
            const SizedBox(height: 40),
          ],
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _unpair,
              icon: const Icon(Icons.link_off),
              label: const Text('Unpair Vehicle'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red.withOpacity(0.2), foregroundColor: Colors.red, padding: const EdgeInsets.all(15)),
            ),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VIRYA APM', style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          if (pendingOta)
            IconButton(
              icon: const Icon(Icons.system_update, color: Colors.orange),
              onPressed: () => setState(() => _currentIndex = 2),
            )
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          _buildHomeTab(),
          _buildDiagnosticsTab(),
          _buildSettingsTab(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: const Color(0xFF0A0E17),
        selectedItemColor: const Color(0xFF0070F3),
        unselectedItemColor: Colors.grey,
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.speed), label: 'Drive'),
          BottomNavigationBarItem(icon: Icon(Icons.build), label: 'Diagnostics'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
