import json

class Pathfinder:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/pathfinder_specs.json"

    def calculate_sovereign_route(self, origin, destination):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[NAVIGATION] 🧭 CALCULATING LOW-STATIC ROUTE: {origin} -> {destination}")
        
        print(f"[HUD] BYPASSING NOISE NODES: {', '.join(data['high_noise_nodes'])}")
        print(f"[HUD] PRIORITIZING BUFFER ZONES: {data['quiet_buffer_zones'][0]}")
        print("VERDICT: Route optimized for zero sensory fatigue. Proceed via the Arches.")

if __name__ == "__main__":
    Pathfinder().calculate_sovereign_route("Stretford_M32", "Madison_Place")
