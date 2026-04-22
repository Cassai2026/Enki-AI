import json
import os

class CharityForensicAuditor:
    def __init__(self):
        self.conflict_data = "enki_ai/game_engine/data/conflict_network.json"
        self.report_dir = "enki_ai/reports"

    def audit_charity_flow(self):
        """
        Identifies 'Circular Extraction' where donations flow back 
        to director-controlled entities.
        """
        with open(self.conflict_data, 'r') as f:
            network = json.load(f)
            
        print(f"--- 🕵️ ANU-EXECUTIVE: CHARITY & CONFLICT AUDIT ---")
        
        # Scan the reports Debbie already has
        reports = [f for f in os.listdir(self.report_dir) if f.startswith('audit_')]
        
        for r_file in reports:
            with open(os.path.join(self.report_dir, r_file), 'r') as f:
                report = json.load(f)
            
            # Check for name matches in the conflict network
            for entry in network:
                for linked_corp in entry['linked_commercial_entities']:
                    # If a Mentee/Audited Company is linked to a Charity Director
                    if linked_corp in str(report.get('raw_data', '')):
                        print(f"[CONFLICT] 🚩 ALERT: Potential Circular Flow detected.")
                        print(f"           Charity: {entry['entity_name']}")
                        print(f"           Commercial Link: {linked_corp}")
                        print(f"           Shared Directors: {entry['directors']}")
                        print(f"           VERDICT: High Risk of 'Static' Wash.")

if __name__ == "__main__":
    auditor = CharityForensicAuditor()
    auditor.audit_charity_flow()
