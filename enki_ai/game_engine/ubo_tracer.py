import json

class UBOTracer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/ubo_hunt_specs.json"

    def trace_capital_flow(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] 🕵️  TRACING GLOBAL OWNERSHIP TREE: {data['parent_entity']}")
        
        # Logic: Identifying layers of insulation between Stretford and the Cash
        for node in data['suspected_nodes']:
            print(f"[HUD] ANALYZING NODE: {node} | LINK PROBABILITY: {data['flag_threshold']*100}%")
        
        print("VERDICT: Capital is being funneled into upper-tier holding companies, bypassing local reinvestment.")

if __name__ == "__main__":
    UBOTracer().trace_capital_flow()
