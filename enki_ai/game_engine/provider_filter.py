import json

class ProviderFilter:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/provider_audit_specs.json"

    def audit_provider_integrity(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SCRUTINY] 🧐 AUDITING VULNERABILITY PROVIDER: {data['provider_id']}")
        
        if data['admin_expense_pct'] > 25.0:
            print(f"🚩 ALERT: HIGH ADMINISTRATIVE CHURN ({data['admin_expense_pct']}%). Money is being trapped in management.")
        
        if data['direct_impact_score'] < 0.5:
            print(f"🚩 ALERT: LOW DIRECT IMPACT. Support is theoretical, not physical.")
        
        print("VERDICT: Provider fails Sovereign Scrutiny. Reallocation recommended.")

if __name__ == "__main__":
    ProviderFilter().audit_provider_integrity()
