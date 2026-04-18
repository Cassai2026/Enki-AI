import json

class CorpMonitor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/corporate_monitor_specs.json"

    def audit_ownership_shifts(self, current_psc):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[GHOST] 🕵️  SCANNING CORPORATE LAYERS...")
        
        if current_psc != data['last_known_ubo']:
            print(f"🚩 ALERT: UBO SHIFT DETECTED. From {data['last_known_ubo']} to {current_psc}.")
            print("ACTION: Cross-reference with BVI Shell Database.")
        else:
            print(f"✅ STATUS: {data['target_entities'][0]} stability confirmed. No stealth shifts.")

if __name__ == "__main__":
    CorpMonitor().audit_ownership_shifts("Chris_Oglesby")
