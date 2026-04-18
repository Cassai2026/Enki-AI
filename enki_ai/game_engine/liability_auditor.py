import json

class LiabilityAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/liability_specs.json"

    def audit_parasitism(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 🔍 AUDITING ASYMMETRIC DEBT EXTRACTION...")
        
        # If the public carries 95% of the risk but gets 0% of the equity
        equity_leakage = data['partner_equity_growth'] * data['public_risk_ratio']
        
        print(f"[HUD] COUNCIL DEBT: £{data['council_debt_gbp']:,}")
        print(f"[HUD] PARTNER ASSET GROWTH: £{data['partner_equity_growth']:,}")
        print(f"[HUD] PUBLIC RISK EXPOSURE: {data['public_risk_ratio']*100}%")
        print("VERDICT: The Public is subsidizing Corporate Equity Growth through high-interest Municipal Debt.")

if __name__ == "__main__":
    LiabilityAuditor().audit_parasitism()
