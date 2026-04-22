import time
import os
import json

class SomaticLogSovereign:
    def __init__(self):
        self.log_path = "enki_ai/game_engine/data/somatic_history.json"
        if not os.path.exists("enki_ai/game_engine/data"):
            os.makedirs("enki_ai/game_engine/data")

    def log_daily_foundation(self, sleep_score, mood_score, energy_level):
        """Part 1 & 4: Energy Mapping and Biological Ledger."""
        entry = {
            "timestamp": time.strftime("%Y-%m-%d"),
            "sleep": sleep_score, # 1-10
            "mood": mood_score,   # 1-10
            "energy": energy_level, # 1-100%
            "status": self._calculate_titan_ratio(sleep_score, energy_level)
        }
        
        print(f"\n[SOMATIC] 🧬 LOGGING BIOLOGICAL ROI...")
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")
            
        return entry

    def _calculate_titan_ratio(self, sleep, energy):
        """Part 2: The Titan-Ratio Logic."""
        # Simple algorithm: High sleep + High energy = TITAN_READY
        ratio = (sleep * 10) + energy
        if ratio > 150:
            return "TITAN_READY"
        elif ratio > 80:
            return "FLOW_MAINTENANCE"
        else:
            return "RECOVERY_MANDATORY"

    def check_recovery_need(self, current_status):
        """Part 3: Recovery Triggers."""
        if current_status == "RECOVERY_MANDATORY":
            print("[HUD] ⚠️  BIO-WARNING: Energy reserves low.")
            print("[HUD] 🛡️  TRIGGERING RECOVERY PROTOCOL: 'Ghost-Cinema' Active.")
            os.system('PowerShell -Command "[Console]::Beep(400, 800)"')
            return True
        print("[HUD] ✅ BIOLOGICAL SHIELD STABLE.")
        return False

if __name__ == "__main__":
    somatic = SomaticLogSovereign()
    # Scenario: Child had poor sleep (4/10) and low energy (30%)
    data = somatic.log_daily_foundation(sleep_score=4, mood_score=5, energy_level=30)
    somatic.check_recovery_need(data["status"])
