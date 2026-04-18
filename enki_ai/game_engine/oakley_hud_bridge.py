import time

class OakleyHUD:
    def __init__(self):
        self.device = "Oakley_Sovereign_Lens"
        self.status = "CONNECTED"

    def push_to_lens(self, message, urgency="NORMAL"):
        """Displays a high-frequency overlay on the Architect's field of vision."""
        color = "CYAN" if urgency == "NORMAL" else "AMBER"
        print(f"\n[HUD] 👓 PROJECTING TO LENS: [{color}] {message}")
        
    def somatic_feedback_loop(self, pulse_rate):
        """Monitors heartbeat via the frames and adjusts the 'Shrink' logic."""
        if pulse_rate > 100:
            self.push_to_lens("Somatic Spike Detected. Initializing Calm Scaffolding.", "HIGH")
            return "ACTIVATE_SHIELD"
        else:
            self.push_to_lens("Vibration Stable. Node 29 is Flowing.")
            return "STABLE"

if __name__ == "__main__":
    hud = OakleyHUD()
    # Simulating a real-time HUD update while walking through Stretford Mall
    hud.somatic_feedback_loop(pulse_rate=105)
