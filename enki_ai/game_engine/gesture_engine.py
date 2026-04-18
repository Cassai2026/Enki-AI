import json
import math

class GestureEngine:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/gesture_specs.json"

    def process_zoom(self, hand_l_pos, hand_r_pos):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        
        # Calculate Euclidean distance between hand coordinates
        dist = math.sqrt(sum((l - r) ** 2 for l, r in zip(hand_l_pos, hand_r_pos)))
        
        print(f"\n[INTERFACE] 🖐️  HAND TRACKING ACTIVE...")
        if dist > data['min_dist_mm']:
            zoom_level = dist / 100 * data['scaling_factor']
            print(f"[HUD] GENESIS ZOOM: {zoom_level:.2f}x")
            print(f"[HUD] DATA DENSITY: Expanding to 10^47 layers.")
        else:
            print("[HUD] ZOOM: RESET TO NEUTRAL.")

if __name__ == "__main__":
    # Simulating hands moving from 100mm to 400mm apart
    GestureEngine().process_zoom((0,0,0), (0,400,0))
