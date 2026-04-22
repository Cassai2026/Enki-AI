import json

class RunoffAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/runoff_toxin_specs.json"

    def audit_neglect(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SHIELD] ☣️  AUDITING KINGSWAY RUNOFF TOXICITY...")
        
        annual_volume_liters = data['road_surface_area_sqm'] * data['avg_rainfall_mm']
        total_toxin_kg = (annual_volume_liters * data['pollutant_load_mg_l']) / 1e6
        
        print(f"[HUD] ANNUAL UNFILTERED RUNOFF: {annual_volume_liters:,} Liters")
        print(f"[HUD] DEPOSITED TOXINS: {total_toxin_kg:.2f} kg/year")
        print("VERDICT: Breach of Environmental Protection Act. Kingsway Engineer is Liable.")

if __name__ == "__main__":
    RunoffAuditor().audit_neglect()
