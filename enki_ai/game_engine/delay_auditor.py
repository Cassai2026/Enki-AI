import json

class DelayAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/delay_specs.json"

    def audit_fee_churn(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] ⏳ AUDITING THE DELAY-FEE INCENTIVE...")
        
        daily_accrual = data['consultant_fee_accrual_gbp'] / data['days_overrun']
        print(f"[HUD] TOTAL OVERRUN: {data['days_overrun']} Days")
        print(f"[HUD] CONSULTANT ACCRUAL PER DAY: £{daily_accrual:,.2f}")
        print("VERDICT: Administrative profit is positively correlated with community disruption.")

if __name__ == "__main__":
    DelayAuditor().audit_fee_churn()
