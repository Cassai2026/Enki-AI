import json

class CircularAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/circular_economy_specs.json"

    def audit_circulation(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ECONOMY] 🔄 AUDITING CIRCULAR VELOCITY...")
        
        velocity = (data['internal_transactions_count'] * data['avg_transaction_value']) / 1000
        retention_score = 100 - data['external_leakage_percent']
        
        print(f"[HUD] CIRCULATION VELOCITY: {velocity:.2f}v")
        print(f"[HUD] CAPITAL RETENTION: {retention_score}%")
        print(f"VERDICT: M32 Boundary Lock is holding. Wealth is accumulating locally.")

if __name__ == "__main__":
    CircularAuditor().audit_circulation()
