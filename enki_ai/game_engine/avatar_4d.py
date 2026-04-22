import math
import time
import os

class HyperAvatar4D:
    def __init__(self, archetype_name):
        self.name = archetype_name
        self.dimensions = 4
        self.rotation_theta = 0

    def render_projection(self, animus_flow_score):
        """
        Simulates a 4D tesseract projection.
        Complexity (edges) scales with Flow Score (1-10).
        """
        self.rotation_theta += 0.1
        # Complexity = how many 'hyper-edges' are visible
        complexity = int(animus_flow_score * 4)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"--- 💠 4D AVATAR SYNC: {self.name.upper()} ---")
        print(f"ANIMUS FLOW: {animus_flow_score}/10 | DIMENSION: {self.dimensions}D")
        
        # Simulating the 4D rotation in ASCII
        # A 4D structure rotating into 3D space looks like expanding/contracting shells
        for i in range(complexity):
            offset = math.sin(self.rotation_theta + i) * 10
            padding = " " * int(abs(offset))
            if i % 2 == 0:
                print(f"{padding}◢▆▅▄▃▂ {self.name} ▂▃▄▅▆◣")
            else:
                print(f"{padding}◥▇▆▅▄▃  SHIELD  ▃▄▅▆▇◤")

    def pulse(self, duration_seconds, stress_level):
        """Adjusts the 4D rotation speed based on stress."""
        flow = 10 - (stress_level / 10)
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            self.render_projection(flow)
            # Higher stress = faster, more chaotic rotation (Static)
            # Lower stress = slow, majestic 4D movement (Flow)
            time.sleep(0.2 if stress_level < 50 else 0.05)

if __name__ == "__main__":
    # Test: Mentee 01 'Graphene Weaver' in a Flow State
    avatar = HyperAvatar4D("Graphene Weaver")
    avatar.pulse(duration_seconds=5, stress_level=20)
