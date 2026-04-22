import random
import time
import os

class ManchesterMissionGenerator:
    def __init__(self):
        self.locations = ["STRETFORD_HUB", "M32_ARCHES", "CITY_CENTRE_CORE", "RECOVERY_PARK"]
        self.materials = ["PET-G", "Graphene Sheet", "Copper Wire", "Silicon Chip"]

    def generate_mission(self, mentee_archetype):
        """Creates a mission tailored to the child's Sovereign Identity."""
        start = random.choice(self.locations)
        end = random.choice([loc for loc in self.locations if loc != start])
        target = random.choice(self.materials)
        
        mission = {
            "title": f"Operation: {target} Retrieval",
            "path": f"{start} -> {end}",
            "objective": f"Secure {target} for the M32 Node Build.",
            "required_module": "STATIC_SENSOR" if "CITY" in end else "FOCUS_LENS"
        }
        
        self.render_briefing(mission, mentee_archetype)
        return mission

    def render_briefing(self, mission, archetype):
        """Visual HUD Briefing for the GTA Underground Simulation."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"==========================================")
        print(f"   📡 MISSION BRIEFING | {archetype.upper()}   ")
        print(f"==========================================")
        print(f" TITLE: {mission['title']}")
        print(f" ROUTE: {mission['path']}")
        print(f" TASK:  {mission['objective']}")
        print(f" TOOL:  Use {mission['required_module']} to mitigate Static.")
        print(f"==========================================")
        print("   (Hold 'HIGH' to Accept Mission | OUSH)  ")
        
        # Audio cue for mission start
        os.system('PowerShell -Command "[Console]::Beep(1200, 200); [Console]::Beep(1500, 300)"')

if __name__ == "__main__":
    gen = ManchesterMissionGenerator()
    # Scenario: Mentee 01 (Graphene Weaver) takes a mission
    gen.generate_mission(mentee_archetype="Graphene Weaver")
