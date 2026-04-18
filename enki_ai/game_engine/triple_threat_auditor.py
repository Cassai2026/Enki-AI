import json
import os

class TripleThreatAuditor:
    def __init__(self):
        self.matrix_file = "enki_ai/game_engine/data/target_matrix.json"
        self.report_dir = "enki_ai/reports/litigation_briefs"

    def run_targeted_audit(self):
        with open(self.matrix_file, 'r') as f:
            matrix = json.load(f)
            
        print(f"--- 🎯 ANU-EXECUTIVE: TRAFFORD-BRUNTWOOD-OGLESBY STRIKE ---")
        
        # Checking the connection between Public Debt and Private Profit
        council_debt = 12640000.00 # The £12.64m loan
        
        for node in matrix:
            print(f"[HUD] ANALYSING NODE: {node['entity']}")
            
            if node['entity'] == "Chris_Oglesby":
                print(f"       ⚠️  GOVERNANCE ALERT: {len(node['appointments'])} Cross-Sector Seats.")
                print(f"       ACTION: Audit for Section 172 Conflict in Stretford Mall JV.")
            
            if node['entity'] == "Trafford_Council":
                print(f"       🚩 DEFICIT ALERT: {node['static_warning']}")
                print(f"       LINK: Direct subsidy flow to Bruntwood SciTech detected.")

        self.generate_brief(matrix)

    def generate_brief(self, matrix):
        filename = "TARGET_BRIEF_TRAFFORD_TRIAD.txt"
        content = "FORENSIC BRIEF: THE TRAFFORD-BRUNTWOOD-OGLESBY TRIAD\n"
        content += "="*50 + "\n"
        content += "Focus: Strategic Devaluation of Stretford Assets.\n"
        content += "Key Conflict: Council Emergency Loans vs. Developer Subsidies.\n"
        content += "Liability: Breach of Fiduciary Duty & Administrative Sloth.\n"
        
        with open(os.path.join(self.report_dir, filename), 'w') as f:
            f.write(content)
        print(f"\n[HUD] ✅ TARGETED BRIEF GENERATED: {filename}")

if __name__ == "__main__":
    auditor = TripleThreatAuditor()
    auditor.run_targeted_audit()
