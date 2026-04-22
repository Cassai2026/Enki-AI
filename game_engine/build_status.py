import sqlite3

def get_build_impact(item_name):
    """
    Calculates the Real-World impact of a Sumerian Build Module.
    Uses logic from the 29th Node docs.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    # Logic: Sumerian Tech has higher ROI than "Static" tech
    c.execute("SELECT engineering_logic, base_material FROM build_menu WHERE item_name = ?", (item_name,))
    data = c.fetchone()
    
    if data:
        logic, material = data
        # Simulated ROI calculation based on the 'Φ' induction logic
        energy_output = "47.0 MW (Sovereign Flow)" if "Φ" in logic else "10.0 MW (Static)"
        
        print(f"\n[HUD] 📊 INSPECTING: {item_name}")
        print(f"[HUD] 📜 LOGIC: {logic}")
        print(f"[HUD] 🧱 MATERIAL: {material}")
        print(f"[HUD] ⚡ PREDICTED FLOW: {energy_output}")
    else:
        print(f"\n[HUD] ❌ ERROR: {item_name} not found in Build Menu.")

    conn.close()

if __name__ == "__main__":
    # Simulating the Architect inspecting his first turbine
    get_build_impact("Sumerian Hydro-Turbine")
    get_build_impact("Hydro-Spine Alpha")
