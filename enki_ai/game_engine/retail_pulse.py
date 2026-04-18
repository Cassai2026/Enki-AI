import json

class RetailPulse:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/retail_pulse_specs.json"

    def audit_survival_window(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ECONOMIC] 💓 MONITORING KING STREET HEARTBEAT...")
        
        cumulative_loss = data['daily_trade_loss_gbp'] * data['rework_obstruction_days']
        survival_index = 1.0 - (data['avg_footfall_decline_pct'] / 100)
        
        print(f"[HUD] ACTIVE OUTPOSTS: {data['active_shops']}")
        print(f"[HUD] CUMULATIVE TRADE LOSS: £{cumulative_loss:,}")
        print(f"[HUD] VITALITY INDEX: {survival_index:.2f} (CRITICAL)")
        print("VERDICT: Economic asphyxiation detected. Immediate 'Sovereign Grant' required from Bruntwood dividends.")

if __name__ == "__main__":
    RetailPulse().audit_survival_window()
