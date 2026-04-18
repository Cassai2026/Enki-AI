import json

class ShellLayerExpander:
    def __init__(self):
        self.offshore_file = "enki_ai/game_engine/data/offshore_network.json"

    def expand_layers(self):
        with open(self.offshore_file, 'r') as f:
            shells = json.load(f)
            
        print(f"--- 🕸️ ANU-EXECUTIVE: SHELL LAYER EXPANSION ---")
        
        for shell in shells:
            depth = shell['layer_depth']
            # Logic: Complexity increases the risk of 'Hidden UBO'
            complexity_score = depth * 3.5
            
            print(f"[NODE] SHELL: {shell['shell_name']}")
            print(f"       LAYERS: {depth} | COMPLEXITY SCORE: {complexity_score}")
            
            if complexity_score > 10:
                print(f"       🚨 STATUS: CRITICAL LAYER MASKING DETECTED.")
                print(f"       ACTION: Initiate UBO Disclosure Demand.")
            print("-" * 30)

if __name__ == "__main__":
    expander = ShellLayerExpander()
    expander.expand_layers()
