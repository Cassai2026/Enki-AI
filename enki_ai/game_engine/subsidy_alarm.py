import json

class SubsidyAlarm:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/subsidy_specs.json"

    def check_subsidy_capture(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[AUDIT] 🚨 SUBSIDY CAPTURE ALARM: {data['subsidy_name']}")
        
        private_benefit = data['amount_gbp'] * data['private_benefit_ratio']
        print(f"[HUD] TOTAL PUBLIC GRANT: £{data['amount_gbp']:,}")
        print(f"[HUD] PRIVATE BENEFIT CAPTURE: £{private_benefit:,}")
        print("VERDICT: High risk of 'Corporate Welfare'. Public funds used to de-risk private assets.")

if __name__ == "__main__":
    SubsidyAlarm().check_subsidy_capture()
