import os
from enki_ai.core.governance import GovernanceEngine

class CodexWriter:
    def __init__(self):
        self.gov = GovernanceEngine()

    def write_new_module(self, filename, content):
        # Law L02: Human Oversight Check
        print(f"\n[CODEX] 📜 PROPOSING NEW MODULE: {filename}")
        confirm = input("Confirm Write to Sovereign Disk? (y/n): ")
        
        if confirm.lower() == 'y' and self.gov.is_permitted("WRITE_MODULE"):
            path = f"enki_ai/game_engine/{filename}.py"
            with open(path, 'w') as f:
                f.write(content)
            print(f"✅ MODULE SEATED AT: {path}")
        else:
            print("❌ WRITE ABORTED.")

if __name__ == "__main__":
    cw = CodexWriter()
    cw.write_new_module("codex_test", "# Enki-Codex v1.0 Alpha\nprint('OUSH')")
