import json

class DivergenceMap:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/borough_divergence_specs.json"

    def audit_wealth_transfer(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[GEOPOLITICS] 🗺️  MAPPING TRAFFORD CAPITAL DIVERGENCE...")
        
        ratio = data['zones']['South_Flagship'] / data['zones']['North_Central']
        print(f"[HUD] SPENDING RATIO (SOUTH vs NORTH): {ratio:.1f}x")
        print(f"[HUD] INFRASTRUCTURE QUALITY GAP: {int((data['infrastructure_quality_index']['South'] - data['infrastructure_quality_index']['North'])*100)}%")
        print("VERDICT: Systematic under-investment in M32 used to subsidize premium upgrades in Tier-1 zones.")

if __name__ == "__main__":
    DivergenceMap().audit_wealth_transfer()
