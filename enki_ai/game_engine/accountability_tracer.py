import json

class AccountabilityTracer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/vetting_specs.json"

    def run_deep_vet(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] 🕵️  CROSS-REFERENCING DIRECTOR ACCOUNTABILITY...")
        
        if data['previous_failures'] > 0 or data['insolvency_history']:
            print(f"🚩 ALERT: 'Phoenix Company' Risk detected. Director has a history of managed failure.")
        
        if data['safety_breaches_logged'] > 0:
            print(f"🚩 CRITICAL: Historical Safety Breaches detected. Responsibility should be denied.")

if __name__ == "__main__":
    AccountabilityTracer().run_deep_vet()
