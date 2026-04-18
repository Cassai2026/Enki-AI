import sqlite3

def handle_gesture(gesture_name):
    """
    Connects MediaPipe hand signals to the Eternius Game World.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    
    if gesture_name == "PINCH":
        print("\n[HUD] 💠 SELECTING NEAREST BUILD SITE...")
        # Pulls the first item from your Build Menu as a selection
        c.execute("SELECT item_name FROM build_menu LIMIT 1")
        item = c.fetchone()[0]
        print(f"[HUD] 🛠️  ATTACHED TO CURSOR: {item}")
        
    elif gesture_name == "SHIELD":
        print("\n[HUD] 🛡️  CLOSING SOVEREIGN OVERLAY. FLOW MODE ACTIVE.")
        
    elif gesture_name == "FIST":
        print("\n[HUD] 💾 SAVING WORLD STATE TO SOVEREIGN LEDGER...")
        
    conn.close()

if __name__ == "__main__":
    # Simulating a "Pinch" gesture detection
    handle_gesture("PINCH")
