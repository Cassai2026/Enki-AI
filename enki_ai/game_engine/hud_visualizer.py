import json

class HUDVisualizer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/visualizer_specs.json"

    def render_toxic_overlay(self, lead_ppm, hydrocarbon_ppm):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[HUD] 🕶️  INITIATING GRAPHENE VISUALIZER OVERLAY...")
        
        # Determine color state based on toxicity
        state = "CRITICAL" if lead_ppm > 5.0 else "FILTERED"
        color = data['color_map']['Lead'] if state == "CRITICAL" else data['color_map']['Pure_H2O']
        
        print(f"[HUD] SCANNING SOIL... DETECTED STATE: {state}")
        print(f"[HUD] RENDERING MESH: {color} (Efficiency: {data['graphene_filter_efficiency']*100}%)")
        print("VERDICT: Visualizing the unseen extraction. OUSH.")

if __name__ == "__main__":
    HUDVisualizer().render_toxic_overlay(12.5, 4.0)
