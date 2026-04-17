import sqlite3


def build_biodome(zone_name, capacity_m2):
    """
    Registers a new closed-ecosystem Biodome in the Eternius build registry.
    Biodomes convert captured CO2 into breathable O2 and provide food yield XP.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # Ensure the atmospheric_stats table exists (seeded by vanguard_deployment)
    c.execute('''CREATE TABLE IF NOT EXISTS atmospheric_stats
                 (id INTEGER PRIMARY KEY, o2_levels REAL, co2_captured REAL, last_update TEXT)''')

    # Register the Biodome as a Build Menu entry
    c.execute("SELECT COUNT(*) FROM build_menu WHERE item_name = ?", (f'Biodome: {zone_name}',))
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO build_menu (item_name, engineering_logic, base_material, purpose) VALUES (?, ?, ?, ?)",
            (
                f'Biodome: {zone_name}',
                'Closed-Loop Carbon Photosynthesis',
                'Polycarbonate Panels & Hydroponic Rails',
                f'Self-Sustaining Ecosystem — {capacity_m2}m²'
            )
        )
        print(f"[HUD] 🌿 BIODOME REGISTERED: {zone_name} ({capacity_m2}m²)")
    else:
        print(f"[HUD] ⚠️  BIODOME ALREADY EXISTS: {zone_name}")

    # Model the O2 output: 1m² of canopy produces ~0.01 units O2/cycle
    o2_yield = round(capacity_m2 * 0.01, 2)
    c.execute(
        "UPDATE atmospheric_stats SET o2_levels = o2_levels + ?, last_update = 'BIODOME CYCLE' WHERE id = 1"
        , (o2_yield,)
    )

    # Award XP to player for the build
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO player_stats (xp_points, tech_unlocked) VALUES (0, 'Starter')")
    xp_gain = int(capacity_m2 * 2)
    c.execute("UPDATE player_stats SET xp_points = xp_points + ?", (xp_gain,))

    conn.commit()
    conn.close()

    print(f"[HUD] 🌬️  O2 YIELD ADDED: +{o2_yield} units/cycle")
    print(f"[HUD] ⚡ XP GAINED: +{xp_gain} (Biodome Construction)")
    print("🚀 BIODOME ONLINE. CLEAN AIR PROTOCOL ACTIVE. OUSH.")


def survey_biodomes():
    """
    Displays all registered Biodomes and the current atmospheric O2 reading.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    print("\n--- 🌿 BIODOME SURVEY ---")
    c.execute("SELECT item_name, purpose FROM build_menu WHERE item_name LIKE 'Biodome:%'")
    rows = c.fetchall()
    if not rows:
        print("No Biodomes registered. Start building! OUSH.")
    for name, purpose in rows:
        print(f" > {name} | {purpose}")

    c.execute("SELECT o2_levels, co2_captured, last_update FROM atmospheric_stats WHERE id = 1")
    atm = c.fetchone()
    if atm:
        print(f"\n[HUD] 🌬️  CURRENT O2 LEVELS: {atm[0]:.2f}")
        print(f"[HUD] 💨 CO2 CAPTURED: {atm[1]:.2f} kg")
        print(f"[HUD] 🕒 LAST UPDATE: {atm[2]}")

    conn.close()


if __name__ == "__main__":
    build_biodome("Mersey Waterfront Alpha", capacity_m2=500)
    build_biodome("Stretford Greenhouse Node", capacity_m2=200)
    survey_biodomes()
