import json
import os

class ManchesterUndergroundMap:
    def __init__(self):
        self.map_data_path = "enki_ai/game_engine/data/manchester_map.json"
        self.nodes = {
            "STRETFORD_HUB": {"coords": [53.447, -2.304], "type": "SAFE_ZONE", "static_level": 2},
            "M32_ARCHES": {"coords": [53.473, -2.253], "type": "RESOURCE_NODE", "static_level": 5},
            "CITY_CENTRE_CORE": {"coords": [53.480, -2.242], "type": "HIGH_STATIC", "static_level": 9},
            "RECOVERY_PARK": {"coords": [53.435, -2.221], "type": "GHOST_CINEMA_NODE", "static_level": 1}
        }

    def sync_to_gta_engine(self):
        """Prepares the coordinates for a GTA V Map Mod (.xml or .json)."""
        print("\n[MAP] 📍 GENERATING MANCHESTER UNDERGROUND MATRIX...")
        
        with open(self.map_data_path, 'w') as f:
            json.dump(self.nodes, f, indent=4)
            
        for name, data in self.nodes.items():
            vibe = "🛡️ PROTECTED" if data['static_level'] < 4 else "⚠️ HIGH STATIC"
            print(f"[HUD] NODE: {name} | VIBE: {vibe} | LVL: {data['static_level']}")

    def get_nearest_safe_zone(self, current_lat, current_lon):
        """Finds the closest recovery point in the simulation."""
        # Simple distance logic for the HUD
        print(f"[HUD] SCANNING MANCHESTER MESH FOR NEAREST SAFE ZONE...")
        return "STRETFORD_HUB"

if __name__ == "__main__":
    manchester = ManchesterUndergroundMap()
    manchester.sync_to_gta_engine()
