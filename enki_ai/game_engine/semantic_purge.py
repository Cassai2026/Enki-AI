import json
import os
import time

class SemanticPurge:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/decay_specs.json"
        self.data_dir = "enki_ai/game_engine/data/"

    def run_decay_sweep(self):
        with open(self.spec_file, 'r') as f: specs = json.load(f)
        print(f"\n[CORE] 🧠 INITIATING RECENCY-WEIGHTED DECAY SWEEP...")
        
        now = time.time()
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                age_days = (now - os.path.getmtime(path)) / (24 * 3600)
                
                # Logic: Decay certainty based on age
                certainty = max(0, 1.0 - (age_days * specs['base_decay_rate']))
                
                status = "FRESH" if certainty > 0.8 else "STALE"
                print(f"[HUD] NODE: {filename:25} | CERTAINTY: {certainty:.2f} | STATUS: {status}")
                
                if status == "STALE":
                    print(f"🚩 ACTION: Re-audit required for {filename}.")

if __name__ == "__main__":
    SemanticPurge().run_decay_sweep()
