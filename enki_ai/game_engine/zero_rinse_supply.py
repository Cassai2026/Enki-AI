import sqlite3

class ZeroRinseSupplyChain:
    def __init__(self, db_path='enki_knowledge.db'):
        self.conn = sqlite3.connect(db_path)
        self.init_supply_ledger()

    def init_supply_ledger(self):
        c = self.conn.cursor()
        # Tracking the journey of goods from Source to Sovereign Node
        c.execute('''CREATE TABLE IF NOT EXISTS supply_flow 
                     (id INTEGER PRIMARY KEY, item_id TEXT, source_node TEXT, 
                      current_markup REAL, rinse_detected BOOLEAN, status TEXT)''')
        self.conn.commit()

    def audit_route(self, item_id, source, destination, markup_percentage):
        """
        Detects 'Static' in the chain.
        Logic: If markup > 5% without physical transformation, it's a Rinse.
        """
        print(f"\n[LOGISTICS] 📦 AUDITING FLOW: {item_id}")
        
        # In the 29th Node, we only allow markups for Labor/Energy, not 'Administration'
        if markup_percentage > 5.0:
            rinse = True
            status = "REDIRECTING_VIA_MESH"
            print(f"[HUD] ❌ RINSE DETECTED: {markup_percentage}% Markup found at 'Middle-Man' node.")
            print(f"[HUD] 🕸️  REROUTING: Bypassing corporate static to direct P2P link.")
        else:
            rinse = False
            status = "FLOW_OPTIMIZED"
            print(f"[HUD] ✅ ZERO-RINSE: Handshake confirmed between {source} and {destination}.")

        c = self.conn.cursor()
        c.execute("""INSERT INTO supply_flow 
                  (item_id, source_node, current_markup, rinse_detected, status) 
                  VALUES (?, ?, ?, ?, ?)""", 
                  (item_id, source, markup_percentage, rinse, status))
        self.conn.commit()

if __name__ == "__main__":
    supply = ZeroRinseSupplyChain()
    # Auditing a shipment of Graphene-PET from the Forge to the Biodome
    supply.audit_route("GPET_BATCH_47", "Genesis_Forge_01", "Biodome_Alpha", 12.5)
