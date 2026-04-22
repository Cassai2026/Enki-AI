import sqlite3

def init_eternius_world():
    """
    Initializes the Bu Eternius Online World-Engine.
    Focus: Ancient Engineering, Mersey Build-Zones, and IRL Quests.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # Building the Tables for the IRL Sims Experience
    c.executescript('''
        CREATE TABLE IF NOT EXISTS build_menu (
            id INTEGER PRIMARY KEY, 
            item_name TEXT, 
            engineering_logic TEXT, 
            base_material TEXT
        );
        CREATE TABLE IF NOT EXISTS quest_log (
            id INTEGER PRIMARY KEY, 
            quest_name TEXT, 
            objective TEXT, 
            zone TEXT
        );
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY, 
            xp_points INTEGER, 
            tech_unlocked TEXT
        );
    ''')

    # Seeding the First Sumerian Engineering Modules
    c.execute("INSERT INTO build_menu (item_name, engineering_logic, base_material) VALUES ('Sumerian Hydro-Turbine', 'Φmersey Induction Constant', 'Oak & Sea Copper')")
    c.execute("INSERT INTO build_menu (item_name, engineering_logic, base_material) VALUES ('Engine Barge V1', 'Babylonian Buoyancy Principles', 'Treated Timber')")

    # Seeding the Initial Quests for the Mersey Corridor
    c.execute("INSERT INTO quest_log (quest_name, objective, zone) VALUES ('The Great Alignment', 'Position the first Hydro-Spine module using the Oakley HUD', 'Mersey Mouth')")
    c.execute("INSERT INTO quest_log (quest_name, objective, zone) VALUES ('Tectonic Mapping', 'Log the kinetic potential of the A56 ruck path', 'Stretford Spine')")

    conn.commit()
    conn.close()
    print("🚀 ETERNIUS WORLD-ENGINE INITIALIZED. THE GRID IS LIVE. OUSH.")

if __name__ == "__main__":
    init_eternius_world()
