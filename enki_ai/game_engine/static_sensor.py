import time
import os
import random

class StaticSensorSovereign:
    def __init__(self):
        # Part 2: Somatic Thresholds (Customizable per child)
        self.db_limit = 75  # Decibels
        self.lux_limit = 500 # Light intensity
        self.is_shielding = False

    def scan_environment(self):
        """Part 1: Real-time scan of Acoustic and Lumen levels."""
        # Simulating hardware sensor input
        current_db = random.randint(40, 95)
        current_lux = random.randint(100, 800)
        
        print(f"\n[SCAN] 📡 AMBIENT DB: {current_db} | LUX: {current_lux}")
        
        # Check thresholds
        if current_db > self.db_limit or current_lux >> self.lux_limit:
            self.trigger_shield(current_db, current_lux)
        else:
            print("[HUD] ✅ ENVIRONMENT STABLE. FLOW MAINTAINED.")

    def trigger_shield(self, db, lux):
        """Part 3: Automatic Muting/Dimming response."""
        self.is_shielding = True
        print(f"[HUD] ⚠️  STATIC OVERLOAD: Sound at {db}dB / Light at {lux}lux")
        print("[HUD] 🛡️  ACTIVATING SOMATIC FILTER...")
        
        # Simulate Oakley Dimming and ANC (Active Noise Cancellation)
        os.system('PowerShell -Command "[Console]::Beep(400, 500)"') # Low freq warning
        os.system('PowerShell -Command "Add-Type –AssemblyName System.Speech; ' +
                  '(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'High static detected. Shielding active.\')"')
        
        self.navigate_to_safe_zone()

    def navigate_to_safe_zone(self):
        """Part 4: Safe-Zone Navigation Logic."""
        print("[HUD] 📍 NAVIGATING TO NEAREST RECOVERY NODE...")
        print("[HUD] 🧭 TURN LEFT IN 20 METERS: 'The Quiet Corner'.")
        # Visual star loop to keep focus
        for i in range(3):
            print("✨ Focus on the star. Follow the path. ✨")
            time.sleep(1)

if __name__ == "__main__":
    sensor = StaticSensorSovereign()
    # Test: Simulating a high-static encounter (like a loud siren or bright lights)
    sensor.scan_environment()
