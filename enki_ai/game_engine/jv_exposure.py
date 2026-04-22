import json

class JVExposure:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/jv_specs.json"

    def draft_transparency_demand(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[LEGAL] ⚖️  DRAFTING JOINT-VENTURE DISCLOSURE...")
        
        demand = f"NOTICE: Under the principle of 'Public Money, Public Interest', we demand the Profit-Share Schedule for {data['jv_name']}.\n"
        demand += "RATIONALE: The Council's debt exposure creates a fiduciary duty to disclose why the Partner is not servicing the municipal interest.\n"
        
        output_path = "enki_ai/reports/litigation_briefs/JV_TRANSPARENCY_DEMAND.txt"
        with open(output_path, "w") as f: f.write(demand)
        print(f"[HUD] ✅ JV DEMAND HARDENED: {output_path}")

if __name__ == "__main__":
    JVExposure().draft_transparency_demand()
