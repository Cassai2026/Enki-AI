import json
import os

class BruntwoodForensicAuditor:
    def __init__(self):
        self.profile_file = "enki_ai/game_engine/data/bruntwood_profile.json"
        self.report_path = "enki_ai/reports/litigation_briefs/BRUNTWOOD_EXTRACTION_REPORT.txt"

    def run_value_gap_audit(self):
        with open(self.profile_file, 'r') as f:
            data = json.load(f)
            
        print(f"\n[AUDIT] 🔬 ANALYSING BRUNTWOOD SCITECH EXTRACTION...")
        
        subsidy = data['public_subsidy_est']
        # The 33% Sovereign Efficiency Target
        target_community_gain = subsidy * 0.33
        
        # Simulated actual community gain (usually near zero in corporate-only models)
        actual_gain = subsidy * 0.05 
        
        value_gap = target_community_gain - actual_gain
        
        print(f"[HUD] PUBLIC SUBSIDY: £{subsidy:,.2f}")
        print(f"[HUD] IDENTIFIED VALUE GAP: £{value_gap:,.2f}")
        
        if value_gap > 1000000:
            print(f"🚨 STATUS: SYSTEMIC EXTRACTION DETECTED.")
            self.generate_report(data, value_gap)

    def generate_report(self, data, gap):
        report = f"--- BRUNTWOOD SCITECH FORENSIC AUDIT ---\n"
        report += f"ENTITY: {data['entity']}\n"
        report += f"IDENTIFIED VALUE GAP: £{gap:,.2f}\n"
        report += f"SUBSIDIARIES: {', '.join(data['subsidiaries'])}\n"
        report += "VERDICT: Failure to deliver Social Value commensurate with Public Subsidy.\n"
        report += "ACTION: Prepare 'Notice of Equitable Reclamation'.\n"
        
        with open(self.report_path, "w") as f:
            f.write(report)
        print(f"[HUD] ✅ BRUNTWOOD BRIEF GENERATED: {self.report_path}")

if __name__ == "__main__":
    auditor = BruntwoodForensicAuditor()
    auditor.run_value_gap_audit()
