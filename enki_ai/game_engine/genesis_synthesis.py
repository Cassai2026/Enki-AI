from gemini_bridge import GeminiBridge
from data_sanitizer import DataSanitizer
import json

class GenesisSynthesis:
    def __init__(self):
        self.bridge = GeminiBridge()
        self.sanitizer = DataSanitizer()
        self.output_path = "enki_ai/reports/GENESIS_STRATEGY_REPORT.txt"

    def run_global_audit(self, local_data_summary):
        print("\n[GENESIS] 🧬 INITIATING GLOBAL SYNTHESIS...")
        
        # 1. Sanitize local data to protect Node 29 secrets
        safe_data = self.sanitizer.sanitize_for_uplink(local_data_summary)
        
        # 2. Consult the Oracle (Gemini) for global context
        prompt = f"Using this data: {safe_data}, provide a global legal and financial risk assessment."
        oracle_wisdom = self.bridge.consult_oracle(prompt)
        
        # 3. Merge and Harden
        report = f"--- GENESIS STRATEGY REPORT: NODE 29 ---\n"
        report += f"LOCAL TRUTH WEIGHT: 90%\n"
        report += f"ORACLE CONTEXT WEIGHT: 10%\n\n"
        report += f"GLOBAL CONTEXT FROM ORACLE:\n{oracle_wisdom}\n\n"
        report += "VERDICT: Sovereign Strategy Hardened via Genesis Bridge.\nOUSH."
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[HUD] ✅ GENESIS REPORT GENERATED: {self.output_path}")

if __name__ == "__main__":
    # Example input: Mapping the Bruntwood/Trafford extraction
    audit_context = "Trafford Council has a £12.64m debt linked to Bruntwood SciTech. Bruntwood uses BVI shell companies. Cass and Debbie are auditing for Section 172 breaches."
    GenesisSynthesis().run_global_audit(audit_context)
