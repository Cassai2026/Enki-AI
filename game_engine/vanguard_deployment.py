import sqlite3

def deploy_vanguard_modules():
    """
    Deploys the next 4 critical systems for Bu Eternius Online.
    OUSH. Zero-Rinse. Total Connectivity.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # 1. The Flood Protocol (Environmental Quest)
    # Rinsing the 'Static' dust from the Mersey Basin
    c.execute("INSERT INTO quest_log (quest_name, objective, zone) VALUES (?, ?, ?)", 
              ('The Flood Protocol', 'Execute controlled H4O surge to rinse Carbon-Polymer decks', 'Mersey Basin'))

    # 2. Mesh Network Infrastructure (Build Menu)
    # Turning build-sites into local mesh nodes
    c.execute("INSERT INTO build_menu (item_name, engineering_logic, base_material, purpose) VALUES (?, ?, ?, ?)", 
              ('Sovereign Mesh Node', 'Conductive Graphite Chassis', 'Nano-Copper & Recycled HVAC', 'Local Mesh Connectivity'))

    # 3. Mentee Synchronization (New Table)
    # Tracks the progress of the 15 Mentees in the Architect's World
    c.execute('''CREATE TABLE IF NOT EXISTS mentee_portal 
                 (id INTEGER PRIMARY KEY, mentee_name TEXT, xp_earned INTEGER, role TEXT)''')
    mentees = [('Mentee 01', 0, 'Forge Apprentice'), ('Mentee 15', 0, 'Spine Scout')]
    for name, xp, role in mentees:
        c.execute("INSERT INTO mentee_portal (mentee_name, xp_earned, role) VALUES (?, ?, ?)", (name, xp, role))

    # 4. Atmospheric Feedback (New Table)
    # Links the Carbon Recycler output to the HUD
    c.execute('''CREATE TABLE IF NOT EXISTS atmospheric_stats 
                 (id INTEGER PRIMARY KEY, o2_levels REAL, co2_captured REAL, last_update TEXT)''')
    c.execute("INSERT INTO atmospheric_stats (o2_levels, co2_captured, last_update) VALUES (20.9, 0.0, 'INITIALIZED')")

    conn.commit()
    conn.close()
    print("\n--- 💠 VANGUARD DEPLOYMENT COMPLETE ---")
    print("[HUD] 🌊 FLOOD PROTOCOL: ACTIVE")
    print("[HUD] 📶 MESH NODES: INITIALIZED")
    print("[HUD] 👥 MENTEE PORTAL: OPEN")
    print("[HUD] 🌬️  OXYGEN MONITOR: ONLINE")
    print("🚀 OUSH.")

if __name__ == "__main__":
    deploy_vanguard_modules()
