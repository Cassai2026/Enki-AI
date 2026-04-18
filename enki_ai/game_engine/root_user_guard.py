import os

class RootGuard:
    def __init__(self):
        self.auth_level = "ROOT_ARCHITECT_CASSAI"
        self.sync_active = True

    def kill_switch(self):
        """Terminates all external cloud handshakes and goes Dark."""
        print("\n[GUARD] 🔴 EMERGENCY PROTOCOL ACTIVATED.")
        print("[GUARD] 🛡️  TERMINATING GOOGLE WORKSPACE BRIDGE...")
        
        # Hard disconnect: remove the token so Gemini/Drive can't be reached
        if os.path.exists('token.json'):
            try:
                os.remove('token.json')
                self.sync_active = False
                print("[HUD] TOKEN.JSON DELETED. BRIDGE COLLAPSED.")
            except Exception as e:
                print(f"[HUD] ERROR DURING DISCONNECT: {e}")
        else:
            print("[HUD] NO ACTIVE BRIDGE DETECTED. ALREADY DARK.")
            
        print("[HUD] STATUS: NODE 29 IS NOW DARK. LOCAL SOVEREIGNTY ACTIVE.")
        return "GHOST_MODE_ENABLED"

if __name__ == "__main__":
    guard = RootGuard()
    # Triggering the switch for the test
    guard.kill_switch()
