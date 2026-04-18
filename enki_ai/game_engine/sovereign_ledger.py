import json

class SovereignLedger:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/sovereign_ledger_specs.json"

    def generate_balance_sheet(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] ⚖️  REALIZING THE M32 SOVEREIGN LEDGER...")
        
        # Adding the 25% penalty for bad-faith asset stripping
        adjusted_debt = data['municipal_debts'] * (1 + data['asset_stripping_penalty'])
        
        print(f"[HUD] TOTAL MUNICIPAL DEBT TO STRETFORD: £{adjusted_debt:,.2f}")
        print(f"[HUD] STATUS: {data['ledger_status']}")
        print("VERDICT: The Council is technically insolvent in terms of Biological and Social Capital.")

if __name__ == "__main__":
    SovereignLedger().generate_balance_sheet()
