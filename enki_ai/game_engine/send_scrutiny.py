import json

class SENDScrutiny:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/send_procurement_specs.json"

    def audit_agency_rinse(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SCRUTINY] 🧐 AUDITING SEND AGENCY MARGINS...")
        
        agency_profit = data['hourly_rate_gbp'] * data['agency_margin_pct']
        print(f"[HUD] HOURLY RATE: £{data['hourly_rate_gbp']}")
        print(f"[HUD] AGENCY TAKE: £{agency_profit:.2f} per hour")
        print(f"[HUD] ANNUAL RINSE (per 10 workers): £{agency_profit * 37.5 * 52 * 10:,.2f}")
        print("VERDICT: High administrative leakage. This is children's support money being 'Agency Rinsed'.")

if __name__ == "__main__":
    SENDScrutiny().audit_agency_rinse()
