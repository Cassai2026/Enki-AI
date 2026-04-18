import json
import os

class OffshoreForensicScanner:
    def __init__(self):
        self.offshore_data = "enki_ai/game_engine/data/offshore_network.json"
        self.report_dir = "enki_ai/reports"

    def scan_for_capital_flight(self):
        """
        Identifies money leaving the 29th Node for offshore shells.
        """
        with open(self.offshore_data, 'r') as f:
            shells = json.load(f)
            
        print(f"--- 🌎 ANU-EXECUTIVE: OFFSHORE & SHELL SCAN ---")
        
        reports = [f for f in os.listdir(self.report_dir) if f.startswith('audit_')]
        
        for r_file in reports:
            with open(os.path.join(self.report_dir, r_file), 'r') as f:
                report = json.load(f)
            
            # Match the audited entity to the offshore shell list
            for shell in shells:
                if shell['parent_entity'] in str(report.get('raw_data', '')):
                    print(f"[LEAKAGE] 🚩 ALERT: Capital Flight Detected.")
                    print(f"           Domestic Entity: {shell['parent_entity']}")
                    print(f"           Offshore Shell: {shell['shell_name']}")
                    print(f"           Jurisdiction: {shell['jurisdiction']}")
                    print(f"           Risk Level: {shell['tax_avoidance_risk']}")
                    print(f"           VERDICT: Breach of Social Value Contract.")

if __name__ == "__main__":
    scanner = OffshoreForensicScanner()
    scanner.scan_for_capital_flight()
