import json

class BreachCalculator:
    def __init__(self):
        self.log_file = "enki_ai/game_engine/data/governance_log.json"

    def calculate_liability(self):
        with open(self.log_file, 'r') as f: data = json.load(f)
        
        print(f"--- ⚖️  ANU-EXECUTIVE: SECTION 172 LIABILITY CHECK ---")
        
        # S172 Factors: (a) Long term (b) Employees (c) Suppliers (d) Community (e) Reputation (f) Fairness
        factors_violated = ["Long-term consequences", "Impact on Community", "High Standards of Business Conduct"]
        
        liability_score = len(factors_violated) * 33.3 # Max 100
        
        print(f"[HUD] ENTITY: {data['entity']}")
        print(f"[HUD] LIABILITY SCORE: {liability_score:.1f}%")
        
        for factor in factors_violated:
            print(f"       🚩 BREACH: {factor}")
        
        return liability_score
