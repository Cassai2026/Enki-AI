import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart';

void main() => runApp(AnuApp());

class AnuApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.black,
        primaryColor: Colors.greenAccent,
      ),
      home: AnuDashboard(),
    );
  }
}

class AnuDashboard extends StatelessWidget {
  // The 'One-Touch Seal' Logic
  void _sealEvidence(BuildContext context) {
    HapticFeedback.vibrate(); // Somatic confirmation
    
    // Create the Fingerprint (The Forensic Hash)
    var timestamp = DateTime.now().toIso8601String();
    var bytes = utf8.encode("MENTEE_01_$timestamp");
    var digest = sha256.convert(bytes);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: Colors.green,
        content: Text("🛡️ EVIDENCE SEALED: ${digest.toString().substring(0, 10)}..."),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("ANU FORENSIC AUDITOR", style: TextStyle(fontSize: 22, color: Colors.greenAccent)),
            SizedBox(height: 10),
            Text("NODE: M32 STRETFORD", style: TextStyle(color: Colors.grey)),
            SizedBox(height: 60),
            
            // THE BIG BUTTON
            GestureDetector(
              onLongPress: () => _sealEvidence(context),
              child: Container(
                width: 220,
                height: 220,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.black,
                  border: Border.all(color: Colors.greenAccent, width: 4),
                  boxShadow: [BoxShadow(color: Colors.greenAccent.withOpacity(0.5), blurRadius: 30)],
                ),
                child: Center(
                  child: Text("HOLD TO\nSEAL", textAlign: TextAlign.center, 
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.greenAccent)),
                ),
              ),
            ),
            
            SizedBox(height: 60),
            
            // QUICK ACCESS MODS
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _modButton("MOD 13", Icons.gavel), // Legal Shield
                _modButton("MOD 07", Icons.visibility), // Ghost Cinema
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _modButton(String label, IconData icon) {
    return Column(
      children: [
        IconButton(icon: Icon(icon, color: Colors.white, size: 30), onPressed: () {}),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.white54)),
      ],
    );
  }
}
