import json
import os

class StructuralNegligenceAuditor:
    def __init__(self):
        self.asset_file = "enki_ai/game_engine/data/stretford_mall_asset.json"
        self.report_path = "enki_ai/reports/litigation_briefs/STRUCTURAL_NEGLIGENCE_REPORT.txt"

    def run_negligence_audit(self):
        with open(self.asset_file, 'r') as f:
            asset = json.load(f)
            
        print(f"\n[AUDIT] 🏗️  ANALYSING PHYSICAL DECAY: {asset['asset_name']}")
        
        remediation = asset['estimated_remediation_cost']
        annual_maint = asset['annual_maintenance_budget_est']
        
        # Logic: 10-year cumulative maintenance vs Remediation cost
        ten_year_maint = annual_maint * 10
        negligence_ratio = remediation / ten_year_maint if ten_year_maint > 0 else 100
        
        print(f"[HUD] 10-YEAR MAINT SPEND: £{ten_year_maint:,.2f}")
        print(f"[HUD] REMEDIATION COST: £{remediation:,.2f}")
        print(f"[HUD] NEGLIGENCE RATIO: {negligence_ratio:.1f}x")

        if negligence_ratio > 5:
            print(f"🚨 STATUS: WILFUL NEGLECT DETECTED. Asset is being 'Rinsed'.")
            self.generate_report(asset, negligence_ratio)

    def generate_report(self, asset, ratio):
        report = f"--- FORENSIC STRUCTURAL AUDIT: {asset['asset_name']} ---\n"
        report += f"NEGLIGENCE RATIO: {ratio:.1f}x (Threshold exceeded)\n"
        report += f"OBSERVED DEFECTS: {', '.join(asset['observed_decay_nodes'])}\n"
        report += "LEGAL VERDICT: Breach of Section 4 Landlord and Tenant Act 1985.\n"
        report += "STRATEGY: Use remediation liability to offset 'Sovereign Buyout' price.\n"
        
        with open(self.report_path, "w") as f:
            f.write(report)
        print(f"[HUD] ✅ STRUCTURAL BRIEF GENERATED: {self.report_path}")

if __name__ == "__main__":
    auditor = StructuralNegligenceAuditor()
    auditor.run_negligence_audit()
