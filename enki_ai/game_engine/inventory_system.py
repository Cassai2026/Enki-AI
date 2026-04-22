import sqlite3

def manage_inventory(action, item_name, quantity=1):
    """
    Manages the Architect's materials collected during rucks.
    OUSH. No Static, just raw resources.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # Create Inventory Table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS player_inventory 
                 (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER)''')
    
    if action == "COLLECT":
        # Check if we already have some
        c.execute("SELECT quantity FROM player_inventory WHERE item_name = ?", (item_name,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE player_inventory SET quantity = quantity + ? WHERE item_name = ?", (quantity, item_name))
        else:
            c.execute("INSERT INTO player_inventory (item_name, quantity) VALUES (?, ?)", (item_name, quantity))
        print(f"[HUD] 🎒 COLLECTED: {quantity}x {item_name}")

    elif action == "VIEW":
        print("\n--- 🎒 ARCHITECT'S INVENTORY ---")
        c.execute("SELECT item_name, quantity FROM player_inventory")
        items = c.fetchall()
        if not items:
            print("Inventory Empty. Hit the Mersey and start rucking! OUSH.")
        for name, qty in items:
            print(f"{name}: {qty}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Simulating a successful ruck: Harvesting materials for the Hydro-Turbine
    manage_inventory("COLLECT", "Ancient Oak", 5)
    manage_inventory("COLLECT", "Sea Copper", 10)
    manage_inventory("COLLECT", "Basalt", 2)
    
    # View the current stash
    manage_inventory("VIEW", None)
