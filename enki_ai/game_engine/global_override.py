import json

class GlobalOverride:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/override_specs.json"

    def trigger_sovereign_dark(self, auth_key):
        with open(self.spec_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("❌ ERROR: Specification file corrupted.")
                return
        
        print(f"\n[TERMINAL] ⚠️  INITIATING GLOBAL OVERRIDE...")
        
        if auth_key == data['encryption_key']:
            print("🌑 STATUS: GLOBAL DARK MODE ENGAGED. All nodes encrypted.")
            print("HUD: 'The 29th Node is now Invisible.'")
        else:
            print("❌ ERROR: Authentication Failed. Unauthorized access attempt logged.")

if __name__ == "__main__":
    # In a live scenario, this key is never hardcoded but passed via secure vault
    GlobalOverride().trigger_sovereign_dark("SUMER_M32_ENTROPY")
