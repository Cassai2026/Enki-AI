import json

class FabEngine:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/fab_os_specs.json"

    def execute_print_cycle(self, toxic_load):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FABRICATION] 💎 INITIATING GRAPHENE DEPOSITION...")
        
        # Adjusting infusion based on how much lead is in the runoff
        optimized_rate = data['infusion_rate_mg_s'] * (1 + (toxic_load / 100))
        
        print(f"[HUD] ACTIVE NODES: {data['factory_nodes']} (King Street Local)")
        print(f"[HUD] OPTIMIZED INFUSION: {optimized_rate:.4f} mg/s")
        print("VERDICT: Filter production synchronized with environmental toxicity. OUSH.")

if __name__ == "__main__":
    FabEngine().execute_print_cycle(12.5)
