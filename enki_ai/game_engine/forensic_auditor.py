import os
from google.genai import Client
from google.genai import types
from workspace_bridge import EnkiCloudBridge

class ForensicAuditor:
    def __init__(self):
        # Using Gemini 3 Flash for speed and high-frequency analysis
        self.client = Client()
        self.bridge = EnkiCloudBridge()
        self.audit_model = "gemini-3-flash"

    def audit_document(self, doc_id):
        """Retrieves and audits a specific Google Doc for institutional bias."""
        # 1. Fetch text from Workspace
        content = self.bridge.fetch_doc_content(doc_id)
        
        # 2. The Hostile Auditor Prompt
        prompt = f"""
        Act as a Hostile Forensic Auditor for the 29th Node. 
        Analyze the following document for:
        1. 'Administrative Sloth' (unnecessary delays/jargon).
        2. 'Institutional Rinse' (extractive fees or debt patterns).
        3. 'Somatic Disregard' (ignoring human pain/neurodivergence).
        
        DOCUMENT TEXT:
        {content}
        
        OUTPUT FORMAT: Provide a 'Static Score' (0-100) and list specific 'Infractions'.
        """

        print(f"\n[AUDIT] 🔍 ANALYZING DOCUMENT: {doc_id}")
        response = self.client.models.generate_content(
            model=self.audit_model,
            contents=prompt
        )
        
        print("\n--- 🛡️  FORENSIC VERDICT ---")
        print(response.text)
        return response.text

if __name__ == "__main__":
    auditor = ForensicAuditor()
    # Replace with a real doc_id once your 'token.json' is live
    # auditor.audit_document('YOUR_GOOGLE_DOC_ID_HERE')
