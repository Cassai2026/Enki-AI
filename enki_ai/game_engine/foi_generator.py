import json

class FOIGenerator:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/foi_demand_specs.json"

    def draft_demand(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[LEGAL] 🖋️  DRAFTING SCORCHED-EARTH DISCLOSURE DEMAND...")
        
        demand = f"RE: {', '.join(data['project_codes'])}\n"
        demand += "DEMAND: Pursuant to the FOIA 2000, provide a itemised breakdown of all payments made to EXTERNAL CONSULTANTS.\n"
        demand += "NOTICE: Generic project totals are insufficient. We require the Ledger for individual line items.\n"
        
        output_path = "enki_ai/reports/litigation_briefs/FOI_CONSULTANT_CHURN.txt"
        with open(output_path, "w") as f: f.write(demand)
        print(f"[HUD] ✅ FOI DEMAND HARDENED: {output_path}")

if __name__ == "__main__":
    FOIGenerator().draft_demand()
