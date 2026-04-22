import json

class IntensityCalculator:
    def __init__(self):
        self.network_file = "enki_ai/game_engine/data/heatmap_network.json"

    def calculate_heat(self):
        with open(self.network_file, 'r') as f: data = json.load(f)
        
        print(f"--- 🔥 ANU-EXECUTIVE: CONFLICT INTENSITY MAP ---")
        
        # Logic: Count the connections (links) for each node
        node_heat = {node['id']: 0 for node in data['nodes']}
        for link in data['links']:
            node_heat[link['source']] += 1
            node_heat[link['target']] += 1
            
        for node, score in node_heat.items():
            status = "NORMAL"
            if score >= 3: status = "🚩 HIGH_CONFLICT"
            if score >= 4: status = "☢️  CRITICAL_MONOPOLY"
            
            print(f"[HUD] NODE: {node:20} | LINKS: {score} | STATUS: {status}")
