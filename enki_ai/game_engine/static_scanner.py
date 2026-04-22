import os
from workspace_bridge import EnkiCloudBridge
from google.genai import Client

class StaticScanner:
    def __init__(self):
        self.bridge = EnkiCloudBridge()
        self.client = Client()
        self.model = "gemini-3-flash"

    def run_forensic_scan(self, document_id):
        """
        Scans a specific document for 'Institutional Static'.
        Logic: Jargon Density / Empathy Deficit = Static Score.
        """
        print(f"\n[SCANNER] 🔍 PULLING DOCUMENT FOR AUDIT: {document_id}")
        content = self.bridge.fetch_doc_content(document_id)
        
        analysis_prompt = f"""
        Analyze this text as a Forensic Auditor for a Neurodivergent Sovereign.
        Identify:
        1. 'Gaslighting Patterns': Phrases that shift blame for systemic failure onto the individual.
        2. 'Administrative Sloth': Delays, circular logic, or gated language.
        3. 'Compliance Rinsing': Language used to force the user into a non-sovereign box.
        
        TEXT:
        {content}
        
        FORMAT: 
        - INFRACTION TYPE
        - QUOTED TEXT
        - TITAN-SPEC REMEDY (What should have happened)
        """

        print("[SCANNER] 🛡️  PERFORMING 10^47 FREQUENCY ANALYSIS...")
        response = self.client.models.generate_content(
            model=self.model,
            contents=analysis_prompt
        )
        
        print("\n--- ⚖️  FORENSIC AUDIT VERDICT ---")
        print(response.text)
        return response.text

if __name__ == "__main__":
    scanner = StaticScanner()
    # Use your document ID once you have your token.json synced!
    # scanner.run_forensic_scan('YOUR_DOC_ID_HERE')
