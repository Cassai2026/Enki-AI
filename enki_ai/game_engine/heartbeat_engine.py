import json

class HeartbeatEngine:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/heartbeat_specs.json"

    def pulse_truth(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[BROADCAST] ❤️  PULSING THE SOVEREIGN HEARTBEAT...")
        
        print(f"--- {data['portal_name']} ---")
        for metric in data['live_metrics']:
            print(f"[HUD] LIVE DATA: {metric}")
        
        print("VERDICT: Awareness saturation achieved. The 'Silly Boy' narrative is neutralized.")

if __name__ == "__main__":
    HeartbeatEngine().pulse_truth()
