import hashlib
import time
import json

class EvidenceSealer:
    def __init__(self):
        self.vault_index = "enki_ai/game_engine/data/evidence_vault.json"

    def seal_artifact(self, file_path, category):
        """
        Creates a forensic wrapper for a specific file.
        """
        with open(file_path, "rb") as f:
            bytes = f.read()
            file_hash = hashlib.sha256(bytes).hexdigest()
        
        metadata = {
            "artifact_id": f"NODE29-{int(time.time())}",
            "source_path": file_path,
            "sha256_hash": file_hash,
            "timestamp": time.ctime(),
            "standard": "CPR-PART-31-COMPLIANT",
            "category": category
        }
        
        print(f"\n[VAULT] 🔐 SEALING ARTIFACT: {metadata['artifact_id']}")
        print(f"[HUD] HASH: {file_hash[:16]}...")
        
        return metadata
