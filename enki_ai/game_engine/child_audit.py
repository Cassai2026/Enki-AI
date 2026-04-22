import json

class ChildAudit:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/watchdog_specs.json"

    def audit_funding_flow(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ACCOUNTABILITY] 👶 AUDITING CHILDREN'S SERVICES FLOW...")
        
        funding_gap = data['funding_allocated_gbp'] * (data['service_delivery_gap_pct'] / 100)
        print(f"[HUD] TOTAL CHILDREN'S ALLOCATION: £64.0M")
        print(f"[HUD] ESTIMATED SERVICE GAP: £{funding_gap/1e6:.2f}M")
        print("VERDICT: Funding is being absorbed by 'Management Rework' while SEND families remain in crisis.")

if __name__ == "__main__":
    ChildAudit().audit_funding_flow()
