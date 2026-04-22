import json

class ToxicityInterceptor:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/toxicity_specs.json"

    def run_soil_audit(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SHIELD] ☣️  AUDITING SOIL & WATER TOXICITY...")
        
        for substance, level in data['current_readings'].items():
            if level > data['safety_limit_ppm']:
                print(f"🚩 ALERT: {substance.upper()} EXCEEDS SAFETY LIMITS ({level} ppm).")
                print(f"ACTION: Generate Section 79 EPA Enforcement Notice.")
            else:
                print(f"✅ {substance}: {level} ppm (Safe).")

if __name__ == "__main__":
    ToxicityInterceptor().run_soil_audit()
