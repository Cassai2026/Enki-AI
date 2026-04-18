import json

class WeedTracker:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/weed_tracker_specs.json"

    def calculate_land_devaluation(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[BIOLOGICAL] 🌿 ANALYSING KINGSTREET BANK NEGLECT...")
        
        devaluation = data['weed_density_percent'] * data['remediation_cost_per_sqm']
        print(f"[HUD] INVASIVE SPECIES DETECTED: {', '.join(data['invasive_species'])}")
        print(f"[HUD] ESTIMATED REMEDIATION DEBT: £{devaluation:,.2f}")
        print("VERDICT: The presence of bio-indicators confirms total loss of municipal stewardship.")

if __name__ == "__main__":
    WeedTracker().calculate_land_devaluation()
