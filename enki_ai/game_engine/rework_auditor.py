import json

class ReworkAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/rework_audit_specs.json"

    def calculate_waste(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FINANCE] 💸 AUDITING REGENERATION REWORK WASTE...")
        
        total_waste = data['rework_events'] * data['est_waste_per_rework_gbp']
        
        print(f"[HUD] REWORK CYCLES DETECTED: {data['rework_events']}")
        print(f"[HUD] CUMULATIVE WASTE: £{total_waste:,}")
        print(f"[HUD] DRAINAGE VERDICT: {data['drainage_type'].replace('_', ' ')}")
        print("VERDICT: Failure to implement resin-roads and deep drainage has created a 'Sunk Cost' trap.")

if __name__ == "__main__":
    ReworkAuditor().calculate_waste()
