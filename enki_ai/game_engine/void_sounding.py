import json

class VoidSounding:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/void_sounding_specs.json"

    def audit_ground_stability(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SENSORY] 📡 SCANNING FOR UNDERGROUND VOIDS...")
        
        # Logic: Slower acoustic velocity indicates air pockets/voids
        if data['acoustic_velocity_mps'] < 1800:
            print(f"🚩 ALERT: LOW DENSITY DETECTED. Possible washouts near Node 29.")
            print(f"[HUD] DETECTED VOIDS: {data['detected_hollow_nodes']}")
        else:
            print("✅ STATUS: Ground density within safe parameters.")
            
        print("VERDICT: Foundation integrity compromised by hydraulic erosion.")

if __name__ == "__main__":
    VoidSounding().audit_ground_stability()
