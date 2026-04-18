import json

class EquityPump:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/equity_pump_specs.json"

    def audit_imbalance(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] 🏗️  ANALYSING THE SKYLINE EQUITY PUMP...")
        
        # The ratio of Corporate Asset Growth to Municipal Debt
        pump_ratio = data['partner_assets_gbp'] / data['council_efs_loan_gbp']
        
        print(f"[HUD] PARTNER ASSET VALUE: £{data['partner_assets_gbp'] / 1e9:.2f}B")
        print(f"[HUD] COUNCIL BAILOUT DEBT: £{data['council_efs_loan_gbp'] / 1e6:.1f}M")
        print(f"[HUD] EXTRACTION MULTIPLIER: {pump_ratio:.1f}x")
        print("VERDICT: The 'Shiny' skyline is built on the interest-burdened debt of the outer boroughs.")

if __name__ == "__main__":
    EquityPump().audit_imbalance()
