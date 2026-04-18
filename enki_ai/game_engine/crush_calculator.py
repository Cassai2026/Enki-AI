import json

class CrushCalculator:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/crush_depth_specs.json"

    def calculate_failure_risk(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[PHYSICS] 🏗️  CALCULATING VICTORIAN DRAIN CRUSH DEPTH...")
        
        # Saturated brick loses significant strength
        effective_strength = data['brick_compressive_strength_mpa'] * data['saturation_degradation_factor']
        load_per_sqm = (data['est_weight_tonnes'] * 9.81) / 100 # Distributed over 100sqm footprint
        
        print(f"[HUD] EFFECTIVE BRICK STRENGTH: {effective_strength:.2f} MPa")
        print(f"[HUD] APPLIED LOAD: {load_per_sqm/1000:.2f} MPa")
        
        if (load_per_sqm / 1000) > effective_strength:
            print("🚩 CRITICAL: LOAD EXCEEDS MATERIAL STRENGTH. STRUCTURAL COLLAPSE IMMINENT.")
        else:
            print("⚠️ WARNING: Safety factor below 1.5. Structural fatigue detected.")

if __name__ == "__main__":
    CrushCalculator().calculate_failure_risk()
