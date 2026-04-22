import sqlite3


# Elemental XP multipliers — higher for rarer materials
ELEMENT_MULTIPLIERS = {
    'FIRE': 1.5,   # Thermal energy / forge work
    'WATER': 1.2,  # Hydro-spine operations
    'EARTH': 1.0,  # Rucking / ground-level construction
    'AIR': 1.3,    # Atmospheric and drone operations
}


def trigger_elemental_event(element, intensity):
    """
    Fires an elemental event and converts it into Sovereign XP.
    Elements: FIRE, WATER, EARTH, AIR.
    Intensity: integer 1-10 representing magnitude of the event.
    """
    element = element.upper()
    if element not in ELEMENT_MULTIPLIERS:
        print(f"[HUD] ❌ UNKNOWN ELEMENT: {element}. Must be FIRE, WATER, EARTH, or AIR.")
        return

    multiplier = ELEMENT_MULTIPLIERS[element]
    xp_gain = int(intensity * multiplier * 100)

    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # Ensure player profile exists
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO player_stats (xp_points, tech_unlocked) VALUES (0, 'Starter')")

    c.execute("UPDATE player_stats SET xp_points = xp_points + ?", (xp_gain,))
    c.execute("SELECT xp_points FROM player_stats")
    total_xp = c.fetchone()[0]

    # Log the event into quest_log for the HUD history
    c.execute(
        "INSERT INTO quest_log (quest_name, objective, zone) VALUES (?, ?, ?)",
        (
            f'{element.title()} Event L{intensity}',
            f'Elemental surge recorded — intensity {intensity}/10',
            f'{element.title()} Domain'
        )
    )

    conn.commit()
    conn.close()

    icons = {'FIRE': '🔥', 'WATER': '🌊', 'EARTH': '🌍', 'AIR': '🌬️'}
    print(f"\n[HUD] {icons[element]} ELEMENTAL EVENT: {element} (Intensity {intensity}/10)")
    print(f"[HUD] ⚡ XP GAINED: +{xp_gain} (x{multiplier} multiplier)")
    print(f"[HUD] 📊 TOTAL SOVEREIGN XP: {total_xp}")


def get_elemental_balance():
    """
    Reads the quest_log for all elemental events and prints a balance report.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    print("\n--- 🔮 ELEMENTAL BALANCE REPORT ---")
    totals = {}
    for element in ELEMENT_MULTIPLIERS:
        c.execute(
            "SELECT COUNT(*) FROM quest_log WHERE quest_name LIKE ?",
            (f'{element.title()} Event%',)
        )
        count = c.fetchone()[0]
        totals[element] = count
        icons = {'FIRE': '🔥', 'WATER': '🌊', 'EARTH': '🌍', 'AIR': '🌬️'}
        print(f"[HUD] {icons[element]} {element}: {count} event(s) logged")

    dominant = max(totals, key=lambda k: totals[k]) if any(totals.values()) else 'NONE'
    print(f"\n[HUD] 🏆 DOMINANT ELEMENT: {dominant}")
    conn.close()


if __name__ == "__main__":
    trigger_elemental_event("FIRE", intensity=7)
    trigger_elemental_event("WATER", intensity=5)
    trigger_elemental_event("EARTH", intensity=10)
    get_elemental_balance()
