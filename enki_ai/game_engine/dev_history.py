import json

class DevHistory:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/developer_history_specs.json"

    def audit_evolution(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[HISTORY] 📜 TRACING THE EVOLUTION OF EXTRACTION...")
        
        print(f"[HUD] TRANSITION: {data['foundational_era']} -> {data['modern_era']}")
        print(f"[HUD] DOMINANT PLAYERS: {', '.join(data['key_players'])}")
        print(f"[HUD] CORE DOCTRINE: {data['strategy'].replace('_', ' ')}")
        print("VERDICT: The Developer is no longer a builder; they are a financial instrument designed to extract municipal credit.")

if __name__ == "__main__":
    DevHistory().audit_evolution()
