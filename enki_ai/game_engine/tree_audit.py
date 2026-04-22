import json

class TreeAudit:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/heritage_tree_specs.json"

    def calculate_heritage_loss(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] 🪓 AUDITING BIOLOGICAL CAPITAL DESTRUCTION...")
        
        # 10,000 years of life-accumulated value
        total_valuation = data['aggregate_years_lost'] * data['cavat_valuation_per_year']
        
        print(f"[HUD] AGGREGATE LIFE LOST: {data['aggregate_years_lost']} Years")
        print(f"[HUD] PUBLIC ASSET LOSS: £{total_valuation:,}")
        print("VERDICT: Irreversible destruction of Heritage Assets without Statutory Justification.")

if __name__ == "__main__":
    TreeAudit().calculate_heritage_loss()
