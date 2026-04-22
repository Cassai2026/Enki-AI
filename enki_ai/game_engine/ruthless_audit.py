import json
import os
from anu_executive import AnuExecutiveAssistant

def run_ruthless_cross_ref():
    auditor = AnuExecutiveAssistant()
    
    # Load Vampire Data
    with open("enki_ai/game_engine/data/vampire_vendors.json", "r") as f:
        vampires = json.load(f)
    
    # Scan all Audit Reports in the /reports folder
    report_files = [f for f in os.listdir("enki_ai/reports") if f.startswith('audit_')]
    
    print(f"--- 💀 ANU-EXECUTIVE: RUTHLESS CROSS-REFERENCE ---")
    
    for r_file in report_files:
        with open(os.path.join("enki_ai/reports", r_file), 'r') as f:
            report = json.load(f)
            
        # Check if the Mentee is actually a Vampire Vendor in disguise
        # Or if their 'Static' matches the extraction patterns
        if report['verdict'] == "🚨 STATIC_DETECTED":
            print(f"[AUDIT] 🚩 {report['mentee_id']}: Matches 'Vampire' behavior patterns.")
            print(f"        ACTION: Prepare Section 20 and Financial Forensics.")

if __name__ == "__main__":
    run_ruthless_cross_ref()
