import sqlite3

def update_evolution(steps_taken):
    """
    Converts physical movement into Sovereign XP and unlocks Ancient Tech.
    Includes a 'First Breath' check to initialize stats if empty.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # 1. Ensure a Player Profile exists (First Breath)
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        print("[HUD] 🌱 INITIALIZING ARCHITECT PROFILE...")
        c.execute("INSERT INTO player_stats (xp_points, tech_unlocked) VALUES (0, 'Starter')")
    
    # 2. Add the XP from the Ruck
    xp_gain = steps_taken
    c.execute("UPDATE player_stats SET xp_points = xp_points + ?", (xp_gain,))
    
    # 3. Pull Current Total
    c.execute("SELECT xp_points FROM player_stats")
    current_xp = c.fetchone()[0]
    
    print(f"\n[HUD] ⚡ TECTONIC TREAD ACTIVE: +{xp_gain} XP GAINED")
    print(f"[HUD] 📊 TOTAL SOVEREIGN XP: {current_xp}")
    
    # 4. Evolution Logic: 5000 XP Unlock
    if current_xp >= 5000:
        # Check if already unlocked to avoid duplicate entries
        c.execute("SELECT COUNT(*) FROM build_menu WHERE item_name = 'Hydro-Spine Alpha'")
        if c.fetchone()[0] == 0:
            print("[HUD] 🔓 UNLOCKED: 'Hydro-Spine Alpha' Blueprint available.")
            c.execute("INSERT INTO build_menu (item_name, engineering_logic, base_material) VALUES ('Hydro-Spine Alpha', 'Multi-Node Φmersey Induction', 'Sea Copper & Basalt')")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Simulating the ruck that pushes you into the Alpha tier
    update_evolution(5000)
