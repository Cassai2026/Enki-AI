import sqlite3

class UniversalProfessionHub:
    def __init__(self, db_path='enki_knowledge.db'):
        self.conn = sqlite3.connect(db_path)
        self.init_registry()

    def init_registry(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS profession_registry 
                     (id INTEGER PRIMARY KEY, profession TEXT, enki_module TEXT, mandate TEXT)""")
        
        professions = [
            ('Medicine', 'Sovereign Health', 'Patient Sovereignty > Billing'),
            ('Law', 'Justice Engine', 'Anti-Sloth Legal Forensics'),
            ('Construction', 'Titan-Build', '150% Hardened Infrastructure'),
            ('Arts', 'Waveform Studio', '100% Creator Ownership'),
            ('Education', 'Animus Scaffolding', 'RWL Credit vs Student Debt')
        ]
        
        for p, m, man in professions:
            c.execute("INSERT OR REPLACE INTO profession_registry (profession, enki_module, mandate) VALUES (?,?,?)", (p,m,man))
        
        self.conn.commit()
        print("\n--- 🌐 UNIVERSAL PROFESSION HUB: INITIALIZED ---")
        print("[HUD] ✅ All sectors now align with the 10^47 Frequency.")

    def authorize_trade(self, profession_name):
        """Verifies if a trade is 'Rinse-Free' and Sovereign."""
        c = self.conn.cursor()
        c.execute("SELECT enki_module, mandate FROM profession_registry WHERE profession = ?", (profession_name,))
        row = c.fetchone()
        if row:
            print(f"\n[HUD] 🛡️  TRADE AUTHORIZED: {profession_name}")
            print(f"[HUD] 📜 SYSTEM MODULE: {row[0]}")
            print(f"[HUD] ⚡ PRIMARY MANDATE: {row[1]}")
        else:
            print(f"\n[ALERT] ❌ TRADE REJECTED: {profession_name} is currently operating in 'Static' mode.")

if __name__ == "__main__":
    hub = UniversalProfessionHub()
    hub.authorize_trade('Education')
    hub.authorize_trade('Law')
