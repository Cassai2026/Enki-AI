import json

class BlackHoleAuditor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/black_hole_specs.json"

    def audit_centripetal_drain(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[GEOPOLITICS] 🌌 AUDITING THE MANCHESTER BLACK HOLE...")
        
        inequity_multiplier = data['crane_count_m1'] / max(1, data['crane_count_m32'])
        print(f"[HUD] SKYLINE GROWTH MULTIPLIER (M1 vs M32): {inequity_multiplier}x")
        print(f"[HUD] PERIPHERY DRAIN RATIO: {data['periphery_disinvestment_ratio']}:1")
        print("VERDICT: The survival of the 'Global City' depends on the 'Managed Decline' of the Outer Boroughs.")

if __name__ == "__main__":
    BlackHoleAuditor().audit_centripetal_drain()
