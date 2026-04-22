import json

class InfraGap:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/infra_gap_specs.json"

    def audit_material_theft(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ENGINEERING] 🧱 AUDITING MATERIAL INEQUITY (M32 vs M1)...")
        
        print(f"[HUD] CITY CORE SPEC: {data['city_centre_spec']}")
        print(f"[HUD] STRETFORD SPEC: {data['outer_borough_spec']}")
        print(f"[HUD] COST REDUCTION ON M32: {data['cost_differential_pct']}%")
        print("VERDICT: Stretford is being used as a 'Cost-Saving' dumping ground to de-risk high-end city centre assets.")

if __name__ == "__main__":
    InfraGap().audit_material_theft()
