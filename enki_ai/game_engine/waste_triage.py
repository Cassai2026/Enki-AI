import json

class WasteTriage:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/waste_triage_specs.json"

    def run_reclamation_audit(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[RESOURCE] ♻️  TRIAGING MUNICIPAL WASTE STREAM: {data['source']}")
        
        # Calculation: (Tons * Efficiency) / Weight of one Arch (approx 250kg)
        usable_kg = (data['pet_tonnage_avail'] * 1000) * data['reclamation_efficiency']
        arch_count = int(usable_kg / 250)
        
        print(f"[HUD] USABLE POLYMER: {usable_kg:.2f}kg")
        print(f"[HUD] POTENTIAL ARCHES: {arch_count}")
        print(f"VERDICT: One week of 'waste' equals {arch_count} new structural nodes.")

if __name__ == "__main__":
    WasteTriage().run_reclamation_audit()
