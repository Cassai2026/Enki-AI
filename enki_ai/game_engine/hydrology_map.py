import json

class HydrologyMap:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/hydrology_specs.json"

    def audit_water_integrity(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SUB-SURFACE] 💧 AUDITING MERSEY BASIN HYDROLOGY...")
        
        if data['ph_level'] < 6.0 or data['ph_level'] > 8.0:
            print(f"🚩 ALERT: PH LEAKAGE DETECTED ({data['ph_level']}). Possible industrial runoff.")
        else:
            print(f"✅ STATUS: Soil PH stable at {data['ph_level']}.")
        
        print(f"[HUD] SATURATION: {data['saturation_index']*100}% | AQUIFER: {data['aquifer_depth_m']}m")

if __name__ == "__main__":
    HydrologyMap().audit_water_integrity()
