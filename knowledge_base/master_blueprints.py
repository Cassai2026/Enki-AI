import sqlite3

def flash_master_blueprints():
    """
    Injects the High-Frequency tech into the Eternius Build Menu.
    Indra Vajra, Graphene Suits, and Hydrogen Storage. OUSH.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # 1. The High-Level Blueprints
    blueprints = [
        ('Hydro-Spine Alpha', 'Multi-Node Φmersey Induction', 'Sea Copper & Basalt', 'Energy Generation'),
        ('Hydrogen Battery Node', 'Babylonian Pressure Logic', 'Carbon-Wrapped Steel', 'Energy Storage'),
        ('Indra Vajra Device', '1819-1221 Frequency Bridge', 'Gold-Coated Quartz', 'Frequency Defense'),
        ('Graphene Copper Suit', 'Carbon-Polymer Weave', 'Graphene & Nano-Copper', 'Architect Protection')
    ]
    
    # 2. Update Table Structure for 'Purpose'
    try:
        c.execute("ALTER TABLE build_menu ADD COLUMN purpose TEXT")
    except:
        pass # Column already exists
    
    # 3. Flash the Blueprints
    for item, logic, mat, purpose in blueprints:
        # Avoid duplicates
        c.execute("SELECT COUNT(*) FROM build_menu WHERE item_name = ?", (item,))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO build_menu (item_name, engineering_logic, base_material, purpose) VALUES (?, ?, ?, ?)", 
                      (item, logic, mat, purpose))
            print(f"[HUD] 📜 BLUEPRINT ARCHIVED: {item}")

    conn.commit()
    conn.close()
    print("\n🚀 ALL SOVEREIGN BLUEPRINTS LOADED. THE ARSENAL IS READY. OUSH.")

if __name__ == "__main__":
    flash_master_blueprints()
