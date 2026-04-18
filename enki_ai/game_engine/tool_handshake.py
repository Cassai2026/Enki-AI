import json

class ToolHandshake:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/tool_mesh_specs.json"

    def request_asset(self, tool_type, user_trust):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[COMMERCE] 🛠️  QUERYING TOOL-MESH FOR: {tool_type}")
        
        if user_trust >= data['trust_score_min']:
            print(f"[HUD] ASSET LOCATED: Node_29_Van_04 (300m away).")
            print(f"[HUD] STATUS: Available for Sovereign Exchange.")
        else:
            print("🚩 ALERT: Trust score insufficient for high-value asset.")

if __name__ == "__main__":
    ToolHandshake().request_asset("SDS_Max_Drill", 0.95)
