import json

class TaxRinse:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/tax_destruction_specs.json"

    def calculate_rinse_value(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 💸 AUDITING THE 7.5% MUNICIPAL RINSE...")
        
        # Real benefit vs. the cost hike
        real_value = data['hike_pct'] * data['benefit_to_local_area']
        
        print(f"[HUD] COUNCIL TAX HIKE: {data['hike_pct']}%")
        print(f"[HUD] REAL VALUE RETURNED TO M32: {real_value:.2f}%")
        print(f"[HUD] ASSET DESTRUCTION MULTIPLIER: {data['destruction_multiplier']}x")
        print("VERDICT: The 7.5% hike is a 'Debt-Servicing Levy' for corporate partnerships, not a service improvement.")

if __name__ == "__main__":
    TaxRinse().calculate_rinse_value()
