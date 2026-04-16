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
    # 1. Connect and Build the Vault
    conn = sqlite3.connect('enki_knowledge.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS sovereign_vault 
                     (id INTEGER PRIMARY KEY, 
                      source TEXT, 
                      content TEXT, 
                      pillar TEXT, 
                      intensity_level INTEGER)''')

    print("🛠️  STARTING SOVEREIGN INGEST... OUSH.")

    # 2. Ingest Docx Files
    if not os.path.exists(docs_folder):
        print(f"❌ ERROR: /{docs_folder} not found. Put your 10 docs in there first!")
        return

    for filename in os.listdir(docs_folder):
        if filename.endswith(".docx"):
            path = os.path.join(docs_folder, filename)
            doc = Document(path)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            
            # 3. 'Pimp' the Logic (Tagging your Animus)
            pillar = "GENERAL_RECORDS"
            intensity = 1
            
            if any(word in full_text for word in ["Rinse", "£172M", "Liability", "Sloth"]):
                pillar = "FORENSIC_AUDIT"
                intensity = 10
            elif any(word in full_text for word in ["Lilieth", "Children", "Jaxson", "Nanna"]):
                pillar = "LILIETH_MANDATE"
                intensity = 47
            elif "Φmersey" in full_text or "Tectonic" in full_text:
                pillar = "SOVEREIGN_PHYSICS"
                intensity = 29

            cursor.execute("""INSERT INTO sovereign_vault 
                              (source, content, pillar, intensity_level) 
                              VALUES (?, ?, ?, ?)""",
                          (filename, full_text, pillar, intensity))
            print(f"💎 FLASHED: {filename} -> Pillar: {pillar}")

    conn.commit()
    conn.close()
    print("🚀 BRAIN LOADED. THE ENKI NODE IS LIVE. OUSH.")

def sovereign_query(query_text):
    """
    The Search Logic for the Oakley HUD.
    Finds the truth in your docs instantly.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    cursor = conn.cursor()
    
    # Search for keywords and return the most intense matches first
    cursor.execute("""SELECT content, pillar FROM sovereign_vault 
                      WHERE content LIKE ? 
                      ORDER BY intensity_level DESC LIMIT 3""", 
                  ('%' + query_text + '%',))
    
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    pimp_the_knowledge_base()
