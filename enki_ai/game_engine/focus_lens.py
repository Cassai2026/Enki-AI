import time
import os
import json

class FocusLensSovereign:
    def __init__(self):
        self.state_file = "enki_ai/game_engine/data/focus_state.json"

    def deconstruct_task(self, big_task, sub_steps):
        """Part 1 & 4: Deconstruction and Persistence."""
        # sub_steps should be a list of 5 tiny actions
        mission = {
            "title": big_task,
            "steps": sub_steps,
            "current_index": 0,
            "timestamp": time.time()
        }
        self._save_focus(mission)
        print(f"\n[FOCUS] 🔍 LENS ACTIVE: {big_task}")
        self.render_step(mission)

    def _save_focus(self, data):
        with open(self.state_file, 'w') as f:
            json.dump(data, f)

    def render_step(self, mission):
        """Part 2: The One-at-a-Time HUD."""
        idx = mission["current_index"]
        steps = mission["steps"]
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"--- 🎯 SOVEREIGN FOCUS: {mission['title']} ---")
        print("\n[HUD] CURRENT MICRO-NODE:")
        print(f"👉 {steps[idx].upper()}")
        print(f"\n[ {idx+1} / {len(steps)} ]")
        
        # Hide future steps to stop Animus Static
        print("\n(Future steps are shielded. Focus on the Now.)")

    def complete_micro_step(self):
        """Part 3: Animus Reward Sync."""
        with open(self.state_file, 'r') as f:
            mission = json.load(f)
            
        mission["current_index"] += 1
        
        # Success Audio
        os.system('PowerShell -Command "[Console]::Beep(1500, 150); [Console]::Beep(1800, 150)"')
        print("\n[HUD] ✨ MICRO-NODE COMPLETE. DOPAMINE ANCHOR ACTIVE.")
        
        if mission["current_index"] < len(mission["steps"]):
            self._save_focus(mission)
            time.sleep(1)
            self.render_step(mission)
        else:
            print(f"\n[HUD] 🏆 MISSION ACCOMPLISHED: {mission['title']}")
            os.system('PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'Great work. Mission complete.\')"')

if __name__ == "__main__":
    lens = FocusLensSovereign()
    # Scenario: Building a Graphene Node
    steps = [
        "Pick up one graphene sheet",
        "Place it on the M32 Grid",
        "Align the corner magnets",
        "Click the lock mechanism",
        "Celebrate your first Node"
    ]
    lens.deconstruct_task("Build PET-Graphene Node", steps)
    # Simulating the completion of the first micro-step
    time.sleep(2)
    lens.complete_micro_step()
