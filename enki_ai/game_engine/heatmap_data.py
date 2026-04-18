import json
import os

class HeatmapDataSeater:
    def __init__(self):
        self.output_file = "enki_ai/game_engine/data/heatmap_network.json"

    def seat_network(self):
        """
        Formats the Triad (Trafford, Bruntwood, Oglesby) into a 
        relational network.
        """
        network = {
            "nodes": [
                {"id": "Chris_Oglesby", "group": 1, "label": "Director / CEO"},
                {"id": "Trafford_Council", "group": 2, "label": "Public Body"},
                {"id": "Bruntwood_SciTech", "group": 3, "label": "Developer"},
                {"id": "Stretford_Mall_JV", "group": 3, "label": "Joint Venture"},
                {"id": "BVI_Shell_A", "group": 4, "label": "Offshore Shell"}
            ],
            "links": [
                {"source": "Chris_Oglesby", "target": "Bruntwood_SciTech", "value": 10},
                {"source": "Chris_Oglesby", "target": "Stretford_Mall_JV", "value": 10},
                {"source": "Trafford_Council", "target": "Stretford_Mall_JV", "value": 8},
                {"source": "Bruntwood_SciTech", "target": "BVI_Shell_A", "value": 5},
                {"source": "Trafford_Council", "target": "Bruntwood_SciTech", "value": 7}
            ]
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(network, f, indent=4)
            
        print(f"\n[SCAN] 🕸️  NETWORK NODES SEATED: {len(network['nodes'])} entities mapped.")
