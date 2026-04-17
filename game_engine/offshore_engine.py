import sqlite3


# Offshore zone registry — Mersey Estuary nodes
OFFSHORE_ZONES = [
    'Mersey Mouth',
    'Estuary Alpha',
    'Deep Channel Node',
    'Offshore Spine Rig',
    'Tidal Gateway'
]


def deploy_offshore_rig(rig_name, zone, depth_m, output_kw):
    """
    Registers an offshore energy rig in the Eternius build system.
    Each rig contributes energy output and sovereign XP.
    """
    if zone not in OFFSHORE_ZONES:
        print(f"[HUD] ⚠️  UNKNOWN ZONE: {zone}. Registering anyway — uncharted territory.")

    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # Ensure offshore_rigs table exists
    c.execute('''CREATE TABLE IF NOT EXISTS offshore_rigs
                 (id INTEGER PRIMARY KEY,
                  rig_name TEXT,
                  zone TEXT,
                  depth_m REAL,
                  output_kw REAL,
                  status TEXT DEFAULT 'ACTIVE')''')

    c.execute("SELECT COUNT(*) FROM offshore_rigs WHERE rig_name = ?", (rig_name,))
    if c.fetchone()[0] > 0:
        print(f"[HUD] ⚠️  RIG ALREADY DEPLOYED: {rig_name}")
        conn.close()
        return

    c.execute(
        "INSERT INTO offshore_rigs (rig_name, zone, depth_m, output_kw) VALUES (?, ?, ?, ?)",
        (rig_name, zone, depth_m, output_kw)
    )

    # Mirror into build_menu for HUD visibility
    c.execute("SELECT COUNT(*) FROM build_menu WHERE item_name = ?", (f'Rig: {rig_name}',))
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO build_menu (item_name, engineering_logic, base_material, purpose) VALUES (?, ?, ?, ?)",
            (
                f'Rig: {rig_name}',
                'Tidal / Hydro Induction at depth',
                'Corrosion-Resistant Steel & Nano-Copper',
                f'{output_kw} kW offshore energy node — {zone}'
            )
        )

    # Award XP: 1 XP per kW of output
    xp_gain = int(output_kw)
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO player_stats (xp_points, tech_unlocked) VALUES (0, 'Starter')")
    c.execute("UPDATE player_stats SET xp_points = xp_points + ?", (xp_gain,))

    conn.commit()
    conn.close()

    print(f"\n[HUD] 🌊 OFFSHORE RIG DEPLOYED: {rig_name}")
    print(f"[HUD] 📍 ZONE: {zone} | DEPTH: {depth_m}m")
    print(f"[HUD] ⚡ OUTPUT: {output_kw} kW")
    print(f"[HUD] 🎮 XP GAINED: +{xp_gain}")
    print("🚀 OFFSHORE ENGINE ACTIVE. THE MERSEY FLOWS. OUSH.")


def get_offshore_grid():
    """
    Displays the full offshore rig grid and total power generation.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    try:
        c.execute("SELECT rig_name, zone, depth_m, output_kw, status FROM offshore_rigs")
        rigs = c.fetchall()
    except sqlite3.OperationalError:
        rigs = []

    print("\n--- 🌊 OFFSHORE ENERGY GRID ---")
    if not rigs:
        print("No offshore rigs deployed. Start the Mersey build! OUSH.")
        conn.close()
        return

    total_kw = 0.0
    for rig_name, zone, depth, output, status in rigs:
        print(f" > {rig_name} | {zone} | {depth}m depth | {output} kW | [{status}]")
        total_kw += output

    print(f"\n[HUD] ⚡ TOTAL OFFSHORE OUTPUT: {total_kw:.1f} kW")
    print(f"[HUD] 🌍 EQUIVALENT HOMES POWERED: ~{int(total_kw / 3.5)}")
    conn.close()


if __name__ == "__main__":
    deploy_offshore_rig("Spine Rig Alpha", "Mersey Mouth", depth_m=12.0, output_kw=500)
    deploy_offshore_rig("Tidal Node 01", "Deep Channel Node", depth_m=25.0, output_kw=1200)
    deploy_offshore_rig("Estuary Hub Beta", "Estuary Alpha", depth_m=8.0, output_kw=300)
    get_offshore_grid()
