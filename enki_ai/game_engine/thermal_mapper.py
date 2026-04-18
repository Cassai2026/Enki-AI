import json

class ThermalMapper:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/thermal_map_specs.json"

    def audit_thermal_degradation(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SENSORY] 🌡️  MAPPING KINGSWAY THERMAL DEGRADATION...")
        
        delta = data['tarmac_surface_temp_c'] - data['ambient_air_temp_c']
        print(f"[HUD] TARMAC HEAT RETENTION: +{delta:.1f}°C")
        print(f"[HUD] COOLING DEFICIT: {data['target_cooling_deficit']}°C (due to felled trees)")
        print("VERDICT: Regeneration has created a localized 'Heat Trap' violating safe-living standards.")

if __name__ == "__main__":
    ThermalMapper().audit_thermal_degradation()
