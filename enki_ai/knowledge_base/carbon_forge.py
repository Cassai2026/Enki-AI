import sqlite3

def initialize_carbon_forge():
    """
    Sets up the Carbon Forge blueprints and the high-grade materials 
    needed for the Architect's 4D workshop.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # 1. Add the Carbon Forge to the Build Menu
    c.execute("SELECT COUNT(*) FROM build_menu WHERE item_name = 'Carbon Forge'")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO build_menu (item_name, engineering_logic, base_material, purpose) 
                  VALUES ('Carbon Forge', 'Sumerian Thermal Induction', 'Refractory Basalt & Graphene Coils', 'Master Crafting Station')""")
        print("[HUD] 🔥 CARBON FORGE BLUEPRINT: ARCHIVED")

    # 2. Populate Inventory with Forge-Grade Materials
    forge_materials = [
        ('Refractory Basalt', 20),
        ('Graphene Coils', 5),
        ('Industrial Diamond Dust', 10),
        ('High-Density Carbon', 50)
    ]

    for item, qty in forge_materials:
        c.execute("SELECT quantity FROM player_inventory WHERE item_name = ?", (item,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE player_inventory SET quantity = quantity + ? WHERE item_name = ?", (qty, item))
        else:
            c.execute("INSERT INTO player_inventory (item_name, quantity) VALUES (?, ?)", (item, qty))
        print(f"[HUD] 🎒 FORGE MATERIAL STOCKED: {qty}x {item}")

    conn.commit()
    conn.close()
    print("\n🚀 THE FORGE IS PRIMED. READY TO SMELT THE 29TH NODE. OUSH.")

if __name__ == "__main__":
    initialize_carbon_forge()
