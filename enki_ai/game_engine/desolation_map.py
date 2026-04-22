import json

class DesolationMap:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/town_centre_desolation_specs.json"

    def generate_impact_report(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SOMATIC] 🏥 ANALYSING COMMUNITY EXTRACTION IMPACT...")
        
        print(f"[HUD] RETAIL VACANCY: {data['vacancy_rate_percent']}%")
        print(f"[HUD] RESIDENT STRESS LEVEL: {data['local_stress_index']*100}% (Critical)")
        print(f"[HUD] NOISE POLLUTION: {data['avg_noise_db']}dB (Chronic Exposure)")
        
        output_path = "enki_ai/reports/STRETFORD_EXTRACTION_REPORT.txt"
        with open(output_path, "w") as f:
            f.write(f"EXTRACTION REPORT: STRETFORD TOWN CENTRE\n")
            f.write(f"RETAIL COLLAPSE: {data['vacancy_rate_percent']}%\n")
            f.write(f"MENTAL HEALTH DEBT: High Cortisol due to perpetual 'Rework' noise.\n")
            f.write(f"BIOLOGICAL THEFT: {data['vacancy_rate_percent']}% reduction in local utility.\n")
            
        print(f"✅ IMPACT REPORT HARDENED: {output_path}")

if __name__ == "__main__":
    DesolationMap().generate_impact_report()
