import json

class DividendTracker:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/dividend_specs.json"

    def calculate_distribution(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ECONOMY] 💰 CALCULATING SOVEREIGN DIVIDEND...")
        
        div_total = data['total_efficiency_gain_gbp'] * data['dividend_rate']
        reinvest_total = data['total_efficiency_gain_gbp'] * data['reinvestment_rate']
        per_mentee = div_total / data['mentee_count']
        
        print(f"[HUD] TOTAL DIVIDEND POOL: £{div_total:,.2f}")
        print(f"[HUD] INFRASTRUCTURE REINVESTMENT: £{reinvest_total:,.2f}")
        print(f"[HUD] PER MENTEE PAYOUT: £{per_mentee:,.2f}")
        print("VERDICT: Capital successfully reclaimed from corporate static.")

if __name__ == "__main__":
    DividendTracker().calculate_distribution()
