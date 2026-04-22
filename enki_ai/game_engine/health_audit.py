import json

class HealthAudit:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/health_liability_specs.json"

    def calculate_tort_liability(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SOMATIC] 🏥 CALCULATING MUNICIPAL HEALTH DEBT...")
        
        total_liability = data['pop_density'] * data['liability_per_resident_gbp']
        
        print(f"[HUD] HEAT STRESS INCREASE: +{data['heat_increase_c']}°C")
        print(f"[HUD] COMMUNITY TORT LIABILITY: £{total_liability:,}")
        print("VERDICT: Breach of Duty of Care via Environment Degradation.")

if __name__ == "__main__":
    HealthAudit().calculate_tort_liability()
