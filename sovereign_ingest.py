# backend/core/knowledge_base/sovereign_ingest.py
import sqlite3
import os
from docx import Document
import re

def pimp_the_knowledge_base(docs_folder="./docs"):
    """
    The Architect's Forge: Flashing the Master Docs into the Animus.
    Zero-Rinse. Zero-Static. 10^47 Frequency.
    """
    # Connect to the Sovereign Vault
    conn = sqlite3.connect('enki_knowledge.db')
    cursor = conn.cursor()

    # Create the Triple-Redundancy Tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS sovereign_vault 
                     (id INTEGER PRIMARY KEY, 
                      source TEXT, 
                      content TEXT, 
                      pillar TEXT, 
                      intensity_level INTEGER)''')

    print("🛠️  STARTING SOVEREIGN INGEST... OUSH.")

    for filename in os.listdir(docs_folder):
        if filename.endswith(".docx"):
            path = os.path.join(docs_folder, filename)
            doc = Document(path)
            
            # Extract raw truth from the doc
            full_text = "\n".join([para.text for para in doc.paragraphs])
            
            # Logic to "Pimp" the tagging based on your specific terminology
            pillar = "Foundational"
            intensity = 1
            
            if "Rinse" in full_text or "£172M" in full_text:
                pillar = "FORENSIC_AUDIT"
                intensity = 10  # High Alert: Structural Sloth detected
            elif "Lilieth" in full_text or "Children" in full_text:
                pillar = "LILIETH_MANDATE"
                intensity = 47  # Max Frequency: Protection Protocol
            elif "Tectonic" in full_text or "47k" in full_text:
                pillar = "BIOLOGICAL_ROI"
                intensity = 5   # Physical Layer: The Tread
            
            cursor.execute("""INSERT INTO sovereign_vault 
                              (source, content, pillar, intensity_level) 
                              VALUES (?, ?, ?, ?)""",
                          (filename, full_text, pillar, intensity))
            
            print(f"💎 FLASHED: {filename} -> Pillar: {pillar} (Power: {intensity})")

    conn.commit()
    conn.close()
    print("🚀 BRAIN LOADED. THE ENKI NODE IS LIVE. OUSH.")

if __name__ == "__main__":
    pimp_the_knowledge_base()
