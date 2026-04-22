import os
import datetime

class EvidenceVault:
    def __init__(self):
        self.vault_path = "enki_ai/reports/evidence_vault/"
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)

    def secure_artifact(self, artifact_name, content):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_{artifact_name}.txt"
        
        with open(os.path.join(self.vault_path, filename), "w") as f:
            f.write(f"--- SECURE ARTIFACT: {artifact_name} ---\n")
            f.write(f"TIMESTAMP: {timestamp}\n")
            f.write(f"SOURCE: Enki-AI Forensic Auditor\n\n")
            f.write(content)
            
        print(f"[HUD] ✅ ARTIFACT SECURED IN VAULT: {filename}")

if __name__ == "__main__":
    vault = EvidenceVault()
    vault.secure_artifact("BRUNTWOOD_LOAN_SNAPSHOT", "Evidence of £12.64m loan structure via Trafford Council.")
