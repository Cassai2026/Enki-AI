import json

class CanopyAudit:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/canopy_deficit_specs.json"

    def calculate_environmental_debt(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ECOLOGY] 🌳 AUDITING STRETFORD CANOPY EXTRACTION...")
        
        # Financial value of a mature tree in an urban environment is approx £15k
        financial_loss = data['mature_trees_removed'] * 15000
        recovery_time_years = 25 
        
        print(f"[HUD] TOTAL MATURE TREES LOST: {data['mature_trees_removed']}")
        print(f"[HUD] ESTIMATED ASSET VALUE STRIPPED: £{financial_loss:,}")
        print(f"[HUD] THERMAL INCREASE: +{data['cooling_effect_loss_c']}°C due to Tarmac surfacing.")
        print("VERDICT: Regeneration has created a permanent Ecological Debt.")

if __name__ == "__main__":
    CanopyAudit().calculate_environmental_debt()
