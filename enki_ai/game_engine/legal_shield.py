import json
import os
import time

class SovereignIncidentLedger:
    def __init__(self, mentee_id):
        self.mentee_id = mentee_id
        self.log_path = f"enki_ai/game_engine/data/legal_event_{int(time.time())}.json"

    def record_event(self, interaction_type="AUTHORITY_CONTACT"):
        """
        Part 1: Contemporaneous Logging.
        Records the 'who, what, where' without audio/video risk.
        This is admissible as a 'first-hand account' in UK law.
        """
        event_data = {
            "timestamp": time.ctime(),
            "mentee_id": self.mentee_id,
            "event_type": interaction_type,
            "status": "SOVEREIGN_ASSERTED",
            "location_snapshot": "STRETFORD_NODE_M32" # Placeholder for GPS
        }
        
        with open(self.log_path, 'w') as f:
            json.dump(event_data, f, indent=4)
            
        print(f"[SHIELD] 🔒 INCIDENT LEDGER LOCKED: {self.log_path}")
        self.display_rights_static()

    def display_rights_static(self):
        """Part 2: The Physical Shield."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==========================================")
        print("🛡️  OFFICIAL DISABILITY NOTICE  🛡️")
        print("==========================================")
        print("I AM NEURODIVERGENT (AUTISM).")
        print("UNDER THE EQUALITY ACT 2010, I REQUIRE:")
        print("1. Clear, slow communication.")
        print("2. No physical contact without warning.")
        print("3. My Advocate (Architect) to be present.")
        print("==========================================")
        print("[ID: NODE-29-TITAN] | [STATUS: LOGGED]")
