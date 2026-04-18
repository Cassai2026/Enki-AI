import json
import os

class EnvironmentalTortCalculator:
    def __init__(self):
        self.data_file = "enki_ai/game_engine/data/tort_baseline.json"
        self.output_path = "enki_ai/reports/litigation_briefs/ENVIRONMENTAL_TORT_CLAIM.txt"

    def calculate_liability(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            
        print(f"\n[AUDIT] ⚖️  CALCULATING GENERATIONAL TORT LIABILITY...")
        
        # Logic: (Residents * Exposure) + (Decay Nodes * Devaluation Factor)
        # We value one 'Life-Year' lost at £50,000 (standard UK legal metric)
        health_impact = data['residents_exposed'] * (data['excess_no2_percent'] / 100) * 1000  # Simplified metric
        structural_loss = data['infrastructure_failure_nodes'] * 5000000 # £5m per major node
        
        total_liability = health_impact + structural_loss
        
        print(f"[HUD] HEALTH LIABILITY: £{health_impact:,.2f}")
        print(f"[HUD] STRUCTURAL LOSS: £{structural_loss:,.2f}")
        print(f"[HUD] TOTAL TORT CLAIM: £{total_liability:,.2f}")

        self.generate_tort_brief(total_liability)

    def generate_tort_brief(self, total):
        report = f"--- CLASS ACTION BRIEF: ENVIRONMENTAL TORT ---\n"
        report += f"TOTAL QUANTIFIED LIABILITY: £{total:,.2f}\n"
        report += "CAUSE OF ACTION: Negligence in Duty of Care & Statutory Nuisance.\n"
        report += "DEFENDANTS: Trafford Council, Bruntwood SciTech, ECP Waste JV.\n"
        report += "REMEDY SOUGHT: Full site remediation and Sovereign Land Transfer.\n"
        
        with open(self.output_path, "w") as f:
            f.write(report)
        print(f"[HUD] ✅ TORT BRIEF HARDENED: {self.output_path}")

if __name__ == "__main__":
    calc = EnvironmentalTortCalculator()
    calc.calculate_liability()
