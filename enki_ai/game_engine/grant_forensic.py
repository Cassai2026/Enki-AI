import json

class GrantForensic:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/grant_forensic_specs.json"

    def run_extraction_audit(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SCAN] 🕵️  AUDITING CHARITABLE EXTRACTION: {data['grant_name']}")
        
        extraction_ratio = data['admin_consultant_cost'] / data['total_awarded']
        
        print(f"[HUD] TOTAL GRANT: £{data['total_awarded']:,.2f}")
        print(f"[HUD] EXTRACTION RATIO: {extraction_ratio*100:.1f}%")
        
        if extraction_ratio > 0.33:
            print(f"🚩 ALERT: SYSTEMIC CHARITABLE EXTRACTION DETECTED.")
            print("ACTION: Draft 'Demand for Fund Re-Allocation' for Debbie.")

if __name__ == "__main__":
    GrantForensic().run_extraction_audit()
