import json

class LeakageAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/leakage_specs.json"

    def audit_leakage(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 💸 AUDITING ECONOMIC LEAKAGE FROM STRETFORD...")
        
        print(f"[HUD] ESTIMATED PROFIT EXTRACTION: £{data['estimated_profit_gbp']:,}")
        print(f"[HUD] ACTUAL LOCAL REINVESTMENT: £{data['local_reinvestment_actual']:,}")
        print(f"[HUD] LEAKAGE RATIO: {data['leakage_ratio']*100}%")
        print("VERDICT: The regeneration model is designed for 98% Capital Export.")

if __name__ == "__main__":
    LeakageAuditor().audit_leakage()
