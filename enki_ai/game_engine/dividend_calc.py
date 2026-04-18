import json

class DividendCalc:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/dividend_specs.json"

    def calculate_reclamation(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SOVEREIGN] 💰 CALCULATING THE COMMUNITY DIVIDEND...")
        
        print(f"[HUD] TOTAL DEVELOPMENT VALUE: £{data['total_development_value']:,}")
        print(f"[HUD] DIVIDEND OWED TO STRETFORD: £{data['community_dividend_due']:,}")
        print("VERDICT: This amount represents the 'Theft of Opportunity' currently sitting in Corporate accounts.")

if __name__ == "__main__":
    DividendCalc().calculate_reclamation()
