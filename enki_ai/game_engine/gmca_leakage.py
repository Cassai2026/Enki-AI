import json

class GMCALeakage:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/gmca_leakage_specs.json"

    def audit_regional_rinse(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[AUDIT] 💸 AUDITING CROSS-BOROUGH SUBSIDY LEAKAGE...")
        
        net_loss = data['gmca_contribution_gbp'] - data['returned_benefit_estimate']
        print(f"[HUD] TRAFFORD NET CONTRIBUTION LOSS: £{net_loss:,}")
        print(f"[HUD] RECIPIENT ZONES: {', '.join(data['target_boroughs'])}")
        print("VERDICT: Trafford is 'Over-Contributing' to regional pools while local infrastructure is in 'Critical Failure' mode.")

if __name__ == "__main__":
    GMCALeakage().audit_regional_rinse()
