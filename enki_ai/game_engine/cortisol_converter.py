import json

class CortisolConverter:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/somatic_stress_specs.json"

    def run_debt_calculation(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SOMATIC] 🧬 AUDITING BIOLOGICAL DEBT: {data['mentee_id']}")
        
        # Logic: Excess Cortisol * Days * Multiplier = Financial Liability
        excess = data['avg_cortisol_nmol_L'] - data['baseline_norm']
        biological_debt = excess * data['stress_exposure_days'] * 50 # £50 per nmol/L/day of life-depletion
        
        print(f"[HUD] EXCESS CORTISOL: {excess:.2f} nmol/L")
        print(f"[HUD] TOTAL BIOLOGICAL DEBT: £{biological_debt:,.2f}")
        print("VERDICT: Administrative stress has caused quantifiable physiological extraction.")

if __name__ == "__main__":
    CortisolConverter().run_debt_calculation()
