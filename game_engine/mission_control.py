import sqlite3
import datetime


# Mission priority tiers
PRIORITY = {1: '🔴 CRITICAL', 2: '🟠 HIGH', 3: '🟡 STANDARD', 4: '🟢 PASSIVE'}


def dispatch_mission(mission_name, objective, zone, priority=3):
    """
    Creates a new active mission and dispatches it to the HUD.
    Priority: 1 (Critical) → 4 (Passive).
    """
    if priority not in PRIORITY:
        priority = 3

    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # Ensure missions table has a status and priority column
    try:
        c.execute("ALTER TABLE quest_log ADD COLUMN status TEXT DEFAULT 'ACTIVE'")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE quest_log ADD COLUMN priority INTEGER DEFAULT 3")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE quest_log ADD COLUMN dispatched_at TEXT")
    except sqlite3.OperationalError:
        pass

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO quest_log (quest_name, objective, zone, status, priority, dispatched_at) "
        "VALUES (?, ?, ?, 'ACTIVE', ?, ?)",
        (mission_name, objective, zone, priority, timestamp)
    )
    mission_id = c.lastrowid

    conn.commit()
    conn.close()

    print(f"\n[HUD] 📡 MISSION DISPATCHED — ID #{mission_id}")
    print(f"[HUD] {PRIORITY[priority]} | {mission_name}")
    print(f"[HUD] 🎯 OBJECTIVE: {objective}")
    print(f"[HUD] 📍 ZONE: {zone}")
    print(f"[HUD] 🕒 TIMESTAMP: {timestamp}")
    print("🚀 MISSION CONTROL ACTIVE. OUSH.")
    return mission_id


def complete_mission(mission_id, xp_reward=500):
    """
    Marks a mission as COMPLETE and awards XP to the Architect.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    c.execute("UPDATE quest_log SET status = 'COMPLETE' WHERE id = ?", (mission_id,))

    # Award XP
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO player_stats (xp_points, tech_unlocked) VALUES (0, 'Starter')")
    c.execute("UPDATE player_stats SET xp_points = xp_points + ?", (xp_reward,))
    c.execute("SELECT xp_points FROM player_stats")
    total_xp = c.fetchone()[0]

    conn.commit()
    conn.close()

    print(f"\n[HUD] ✅ MISSION #{mission_id} COMPLETE")
    print(f"[HUD] ⚡ XP AWARDED: +{xp_reward}")
    print(f"[HUD] 📊 TOTAL SOVEREIGN XP: {total_xp}")


def get_mission_briefing():
    """
    Displays all ACTIVE missions sorted by priority on the HUD.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    print("\n--- 📡 MISSION CONTROL BRIEFING ---")
    try:
        c.execute(
            "SELECT id, quest_name, objective, zone, priority FROM quest_log "
            "WHERE status = 'ACTIVE' ORDER BY priority ASC"
        )
    except sqlite3.OperationalError:
        c.execute("SELECT id, quest_name, objective, zone FROM quest_log")
    rows = c.fetchall()

    if not rows:
        print("No active missions. Dispatch a new one! OUSH.")
    for row in rows:
        mid = row[0]
        name = row[1]
        objective = row[2]
        zone = row[3]
        priority = row[4] if len(row) > 4 else 3
        label = PRIORITY.get(priority, '🟡 STANDARD')
        print(f"\n  [{label}] #{mid} {name}")
        print(f"   → {objective} | Zone: {zone}")

    conn.close()


if __name__ == "__main__":
    mid = dispatch_mission(
        "Sovereign Spine Phase 1",
        "Deploy first Hydro-Turbine module at Mersey Mouth",
        "Mersey Corridor",
        priority=1
    )
    dispatch_mission(
        "Carbon Forge Calibration",
        "Run thermal calibration on Genesis Forge at 750°C",
        "Industrial Hub",
        priority=2
    )
    get_mission_briefing()
    complete_mission(mid, xp_reward=1000)
