import sqlite3

def view_active_quests():
    """
    Queries the Eternius DB to show active missions and build tech.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    print("\n--- 🗺️  ACTIVE QUEST LOG ---")
    c.execute("SELECT quest_name, objective, zone FROM quest_log")
    for q in c.fetchall():
        print(f"Quest: {q[0]}\nGoal: {q[1]}\nZone: {q[2]}\n")

    print("--- 🛠️  ANCIENT BUILD MENU ---")
    c.execute("SELECT item_name, engineering_logic FROM build_menu")
    for b in c.fetchall():
        print(f"Item: {b[0]} | Logic: {b[1]}")

    conn.close()

if __name__ == "__main__":
    view_active_quests()
