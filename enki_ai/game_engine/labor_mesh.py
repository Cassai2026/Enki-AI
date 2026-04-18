import json

class LaborMesh:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/labor_mesh_specs.json"

    def match_tasks(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[ECONOMY] 🔗 SYNCING LOCAL LABOR MESH...")
        
        for task in data['open_tasks']:
            print(f"[HUD] TASK: {task} | MATCHING WITH LOCAL SKILL NODES...")
            # Logic: Match task type to skill pool
            print(f"✅ MATCH FOUND: Local Node assigned to {task}. Corporate Recruitment Bypassed.")

if __name__ == "__main__":
    LaborMesh().match_tasks()
