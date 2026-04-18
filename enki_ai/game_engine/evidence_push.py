from evidence_sealer import EvidenceSealer
from admissibility_engine import AdmissibilityEngine

def execute_formatting():
    sealer = EvidenceSealer()
    formatter = AdmissibilityEngine()
    
    # Sealing the specific litigation briefs we generated
    artifacts = [
        sealer.seal_artifact("enki_ai/reports/litigation_briefs/SECTION_790A_NOTICE.txt", "UBO Disclosure Demand"),
        sealer.seal_artifact("enki_ai/reports/litigation_briefs/S172_PERSONAL_LIABILITY_NOTICE.txt", "Statutory Breach Notice")
    ]
    
    formatter.format_for_court(artifacts)

if __name__ == "__main__":
    execute_formatting()
