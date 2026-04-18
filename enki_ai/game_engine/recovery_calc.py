import json

class RecoveryCalc:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/recovery_specs.json"

    def calculate_lost_opportunity(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 📉 CALCULATING STAGNATION RECOVERY DEBT...")
        
        principal_loss = data['stagnant_days'] * data['lost_trade_per_day']
        total_with_interest = principal_loss * (1 + (data['interest_rate_pct'] / 100))
        
        print(f"[HUD] DAYS OF GHOST WORKS: {data['stagnant_days']}")
        print(f"[HUD] TOTAL ECONOMIC DEBT: £{total_with_interest:,}")
        print("VERDICT: Administrative negligence has suppressed local GDP.")

if __name__ == "__main__":
    RecoveryCalc().calculate_lost_opportunity()
