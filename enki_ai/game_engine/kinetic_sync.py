import json

class KineticSync:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/kinetic_suit_specs.json"

    def run_biometric_sync(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[BIOMETRIC] ⚡ SYNCING KINETIC SUIT: {data['suit_id']}")
        
        total_joules = data['avg_steps_daily'] * data['joules_per_step'] * data['suit_efficiency']
        watt_hours = total_joules / 3600 # Convert to Wh
        
        print(f"[HUD] DAILY GENERATION: {watt_hours:.2f} Wh")
        print(f"[HUD] BIOMETRIC FLOW: {data['heart_rate_avg']} BPM (Optimal)")
        print("STATUS: Human-Battery Interlock Active. You are the generator.")

if __name__ == "__main__":
    KineticSync().run_biometric_sync()
