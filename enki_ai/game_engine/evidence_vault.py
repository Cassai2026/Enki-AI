import json
import os
import hashlib
import time

class MasterEvidenceVault:
    def __init__(self):
        self.source_dir = "enki_ai/reports"
        self.vault_file = "enki_ai/game_engine/data/MASTER_VAULT_INDEX.json"
        self.archive_sig = "10^47-NODE-29-SOVEREIGN"

    def seal_the_vault(self):
        """
        Gathers every forensic artifact created and seals it 
        with a master SHA-256 integrity hash.
        """
        print(f"\n[VAULT] 🔐 INITIATING MASTER SEAL: {self.archive_sig}")
        
        vault_index = {
            "seal_time": time.ctime(),
            "artifacts": []
        }

        # Recursively find all txt and json reports
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith(('.txt', '.json')):
                    file_path = os.path.join(root, file)
                    
                    # Generate file hash
                    with open(file_path, "rb") as f:
                        f_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    vault_index["artifacts"].append({
                        "file": file,
                        "path": file_path,
                        "integrity_hash": f_hash
                    })
                    print(f"[HUD] SEALED: {file}")

        # Save the Master Index
        with open(self.vault_file, "w") as f:
            json.dump(vault_index, f, indent=4)
            
        print(f"\n[HUD] ✅ VAULT SECURED. {len(vault_index['artifacts'])} ARTIFACTS HARDENED.")
        print(f"[HUD] MASTER HASH: {hashlib.sha256(str(vault_index).encode()).hexdigest()}")

if __name__ == "__main__":
    vault = MasterEvidenceVault()
    vault.seal_the_vault()
