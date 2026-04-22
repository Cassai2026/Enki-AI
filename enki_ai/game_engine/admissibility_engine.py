import json
import os

class AdmissibilityEngine:
    def __init__(self):
        self.output_dir = "enki_ai/reports/court_bundles"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def format_for_court(self, artifacts):
        """
        Converts sealed artifacts into a formal Schedule of Evidence.
        """
        print(f"--- 🏛️  ANU-EXECUTIVE: COURT BUNDLE GENERATOR ---")
        
        bundle_content = "SCHEDULE OF EVIDENCE: IN THE HIGH COURT OF JUSTICE\n"
        bundle_content += "RE: SYSTEMIC LIABILITY IN GREATER MANCHESTER\n"
        bundle_content += "="*50 + "\n\n"
        
        for i, art in enumerate(artifacts):
            entry = f"ITEM {i+1}: {art['artifact_id']}\n"
            entry += f"DESCRIPTION: {art['category']}\n"
            entry += f"INTEGRITY HASH: {art['sha256_hash']}\n"
            entry += f"TIMESTAMP: {art['timestamp']}\n"
            entry += "-"*30 + "\n"
            bundle_content += entry
            
        file_path = os.path.join(self.output_dir, "MASTER_COURT_BUNDLE.txt")
        with open(file_path, "w") as f:
            f.write(bundle_content)
            
        print(f"[HUD] ✅ COURT BUNDLE HARDENED: {file_path}")
