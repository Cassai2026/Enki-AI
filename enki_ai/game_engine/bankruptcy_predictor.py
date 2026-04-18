import json

class BankruptcyPredictor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/bankruptcy_specs.json"

    def audit_financial_collapse(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[TITAN] 🕳️  AUDITING THE FINANCIAL EVENT HORIZON...")
        
        print(f"[HUD] COUNCIL TAX HIKE: {data['council_tax_hike_pct']}% (Highest in recent years)")
        print(f"[HUD] EMERGENCY CAPITAL LOAN: £{data['capitalization_loan_gbp']:,}")
        print(f"[HUD] RISK STATUS: {data['risk_level']}")
        print("VERDICT: The Council is on life support while its 'Partners' are reporting billion-pound asset growth.")

if __name__ == "__main__":
    BankruptcyPredictor().audit_financial_collapse()
