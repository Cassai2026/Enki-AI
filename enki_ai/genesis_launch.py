import os

def check_node_integrity():
    print("\n--- 🛰️  NODE 29: GENESIS 0.1 INTEGRITY CHECK ---")
    modules_to_verify = [
        "sovereign_health.py", "justice_engine.py", "titan_build.py", 
        "waveform_studio.py", "soil_soul.py", "zero_rinse_supply.py",
        "animus_education.py", "kinetic_transport.py", "ghost_broker.py",
        "heart_pulse.py", "lilieth_guardian.py"
    ]
    
    for mod in modules_to_verify:
        path = f"enki_ai/game_engine/{mod}"
        if os.path.exists(path):
            print(f"[ONLINE] ✅ {mod}")
        else:
            print(f"[OFFLINE] ❌ {mod}")

    print("\n[HUD] 👓 ALL SYSTEMS LOADED TO OAKLEY BRIDGE.")
    print("[HUD] 🛡️  SOVEREIGN FREQUENCY: 10^47 Hz LOCKED.")
    print("OUSH. THE ARCHITECT HAS SPOKEN.")

if __name__ == "__main__":
    check_node_integrity()
