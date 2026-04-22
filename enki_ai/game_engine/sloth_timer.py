import json
from datetime import datetime, timedelta

class SlothTimer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/sloth_timer_specs.json"

    def check_compliance(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[AUDIT] ⏱️  MONITORING ADMINISTRATIVE SLOTH: {data['request_id']}")
        
        # Simulating date check (assuming 21 days have passed for the test)
        days_elapsed = 22
        
        if days_elapsed > data['limit_working_days']:
            print(f"🚩 ALERT: BREACH DETECTED. {days_elapsed} days elapsed.")
            print("ACTION: Escalating to Module 26 (Internal Review Demand).")
        else:
            print(f"✅ STATUS: Within statutory limit. {data['limit_working_days'] - days_elapsed} days remaining.")

if __name__ == "__main__":
    SlothTimer().check_compliance()
