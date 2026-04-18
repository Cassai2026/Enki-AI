import json

class SciTechTracer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/scitech_specs.json"

    def audit_global_reach(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[FORENSIC] 🌐 TRACING THE SCITECH EMPIRE...")
        
        print(f"[HUD] ASSETS UNDER MANAGEMENT: £{data['total_assets_under_mgmt_gbp'] / 1e9:.1f} Billion")
        print(f"[HUD] KEY SHAREHOLDERS: {', '.join(data['shareholders'])}")
        print(f"[HUD] EXPANSION NODES: {len(data['campus_locations'])} Major UK Tech Hubs")
        print("VERDICT: Stretford is a 'town centre' play, but the real cash is in the 'Knowledge Economy' campuses in Manchester and beyond.")

if __name__ == "__main__":
    SciTechTracer().audit_global_reach()
