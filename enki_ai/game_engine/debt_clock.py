import json

class DebtClock:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/debt_clock_specs.json"

    def execute_real_time_audit(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[TITAN] ⚖️  INITIATING MODULE 100: THE CENTURION DEBT-CLOCK...")
        
        print(f"[HUD] TOTAL TRAFFORD DEBT: £{data['total_pwlb_borrowing']:,}")
        print(f"[HUD] DAILY INTEREST BURDEN: £{data['daily_interest_accrual']:,}")
        print(f"[HUD] DEBT PER HOUSEHOLD: £{data['debt_per_household']:,}")
        print("VERDICT: The Borough is being used as a credit-line for developers. Residents are the collateral.")

if __name__ == "__main__":
    DebtClock().execute_real_time_audit()
