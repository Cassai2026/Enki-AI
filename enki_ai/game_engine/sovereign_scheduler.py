import datetime

class FlowScheduler:
    def __init__(self):
        self.flow_states = {
            "TITAN": ["Audit", "Code", "Strategic Launch"],
            "FLOW": ["Write Thesis", "Research", "Documentation"],
            "RECOVERY": ["Music", "Ghost-Cinema", "Rest"]
        }

    def check_flow(self, energy_level):
        """Suggests tasks based on 0-100 Energy level instead of Clock Time."""
        now = datetime.datetime.now().strftime("%H:%M")
        
        if energy_level > 80:
            state = "TITAN"
        elif energy_level > 40:
            state = "FLOW"
        else:
            state = "RECOVERY"
            
        tasks = self.flow_states[state]
        
        print(f"\n[TIME] ⏳ SYSTEM TIME: {now} | ENERGY: {energy_level}%")
        print(f"[HUD] RECOMMENDED STATE: {state}")
        print(f"[HUD] TARGET TASKS: {', '.join(tasks)}")
        
        return state

if __name__ == "__main__":
    scheduler = FlowScheduler()
    # Testing with a 'Post-Audit' energy level
    scheduler.check_flow(85)
