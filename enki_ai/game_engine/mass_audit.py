import os
import json
from anu_executive import AnuExecutiveAssistant

def run_global_audit():
    auditor = AnuExecutiveAssistant()
    data_dir = "enki_ai/game_engine/data"
    report_dir = "enki_ai/reports"
    
    files = [f for f in os.listdir(data_dir) if f.endswith('_ledger.json')]
    
    print(f"--- 💠 ANU-EXECUTIVE: GLOBAL AUDIT INITIATED ---")
    
    for file in files:
        with open(os.path.join(data_dir, file), 'r') as f:
            mentee = json.load(f)
        
        # Run Forensic Strike
        anomalies = auditor.audit_ledger(mentee['current_ledger'])
        
        # Generate the 'Madison Place' Report
        report = {
            "mentee_id": mentee['mentee_id'],
            "archetype": mentee['archetype'],
            "audit_result": anomalies,
            "verdict": "🚨 STATIC_DETECTED" if isinstance(anomalies, dict) else "✅ SOVEREIGN_STABLE"
        }
        
        with open(os.path.join(report_dir, f"audit_{mentee['mentee_id']}.json"), "w") as f:
            json.dump(report, f, indent=4)
            
        print(f"[HUD] AUDITING {mentee['mentee_id']}: {report['verdict']}")

if __name__ == "__main__":
    run_global_audit()
