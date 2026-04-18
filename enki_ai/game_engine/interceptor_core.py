import json
from boundary_guard import BoundaryLayer
from human_state import HumanState

class EnkiInterceptor:
    def __init__(self):
        self.boundary = BoundaryLayer()
        self.human = HumanState()

    def process_request(self, sector, request_text):
        """
        The Interception Loop.
        Checks the Human's Animus state before allowing a response.
        """
        # 1. Pull current Human State (Simulated data for now)
        # In a live build, this would poll your Oakley/Phone sensors
        current_load = 88  # Architect is in High-Focus/Stress
        self.human.update_state(load=current_load, energy=45, pain=True)
        
        current_context = {
            "load": self.human.state["cognitive_load"],
            "sector": sector
        }

        # 2. Consult the Boundary Layer
        verdict = self.boundary.check_intervention(current_context)

        print(f"\n[INTERCEPTOR] 🛰️  SCANNING REQUEST: '{request_text[:30]}...'")
        print(f"[INTERCEPTOR] ⚖️  VERDICT: {verdict}")

        # 3. Execution Logic
        if "SILENCE_AND_REGULATE" in verdict:
            return "[LILIETH SYSTEM MUTE] 🛡️ Output blocked. Cognitive load too high. Grounding protocols engaged. Breathe, Architect."
        
        if "ADVISE_ONLY" in verdict:
            return f"[SOVEREIGN ADVISORY] 📜 Sector: {sector}. Enki cannot decide. Human Agency required for execution."

        return f"[ENKI PROCEED] ✅ Context safe. Generating scaffold for: {request_text}"

if __name__ == "__main__":
    interceptor = EnkiInterceptor()
    
    # Test 1: High Stress / High Load Intervention
    print(interceptor.process_request("GENERAL", "Generate 50 more modules right now!"))
    
    # Test 2: Legal Sector Agency Check
    print(interceptor.process_request("LEGAL", "Should I sign this contract?"))
