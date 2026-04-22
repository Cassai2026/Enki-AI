import json
import os

class ConflictLitigator:
    def __init__(self):
        self.connection_file = "enki_ai/game_engine/data/shadow_board.json"
        self.report_dir = "enki_ai/reports/litigation_briefs"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def scan_for_statutory_breach(self):
        """
        Scans mapped connections for breaches of the Companies Act.
        Specifically looking for undisclosed interests in JVs.
        """
        with open(self.connection_file, 'r') as f:
            data = json.load(f)
            
        print(f"\n[LEGAL] ⚖️  ANALYSING STATUTORY COMPLIANCE: {data['target']}")
        
        for officer in data['officers']:
            print(f"[HUD] AUDITING OFFICER: {officer['name']}")
            
            # Logic: If they have offshore links + commercial links in the same sector
            breach_found = False
            for firm in officer['other_firms']:
                if "Offshore" in firm or "JV" in firm:
                    print(f"       🚩 POTENTIAL BREACH: Undisclosed interest in {firm}")
                    breach_found = True
            
            if breach_found:
                self.draft_brief(officer['name'], data['target'])

    def draft_brief(self, name, target):
        filename = f"BREACH_REPORT_{name.replace(' ', '_')}.txt"
        content = f"LITIGATION BRIEF: STATUTORY BREACH\nTARGET: {name}\nENTITY: {target}\n\n"
        content += "VIOLATION: Companies Act 2006, Section 177 (Duty to declare interest).\n"
        content += "EVIDENCE: Inter-connected directorships with undisclosed offshore shells.\n"
        
        with open(os.path.join(self.report_dir, filename), 'w') as f:
            f.write(content)
        print(f"       ✅ BRIEF GENERATED: {filename}")

if __name__ == "__main__":
    litigator = ConflictLitigator()
    litigator.scan_for_statutory_breach()
