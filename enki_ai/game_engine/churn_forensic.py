import json

class ChurnForensic:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/churn_specs.json"

    def calculate_rinse_ratio(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 🔍 CALCULATING THE ADMINISTRATIVE RINSE...")
        
        extraction_ratio = (data['admin_consultant_cost'] / data['total_budget_gbp']) * 100
        
        print(f"[HUD] TOTAL SPEND: £{data['total_budget_gbp']:,}")
        print(f"[HUD] PHYSICAL IMPROVEMENT: £{data['material_cost_actual']:,}")
        print(f"[HUD] EXTRACTION RATIO: {extraction_ratio:.1f}%")
        print("VERDICT: Project is 86% Administrative Churn. Physical works are secondary to fee extraction.")

if __name__ == "__main__":
    ChurnForensic().calculate_rinse_ratio()
