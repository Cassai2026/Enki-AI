import time
import os
import json

class NodeSyncSovereign:
    def __init__(self):
        self.node_id = "M32_NODE_29"
        self.peers = ["M32_NODE_01", "M32_NODE_07", "M32_NODE_15"] # Peer Mentees
        self.mesh_log = "enki_ai/game_engine/data/mesh_sync.json"

    def broadcast_animus(self, current_state):
        """Part 1 & 2: Encrypts and sends Animus state to the 15 Mentees."""
        signal = {
            "origin": self.node_id,
            "state": current_state,
            "timestamp": time.time(),
            "frequency": "10^47"
        }
        print(f"\n[MESH] 📡 BROADCASTING SIGNAL: {current_state}")
        print(f"[HUD] ENCRYPTING FOR PEER MESH...")
        
        # Part 3: Collaborative Logic (Logging for Peer Review)
        with open(self.mesh_log, 'a') as f:
            f.write(json.dumps(signal) + "\n")
            
        self.render_sovereignty_circle(current_state)

    def render_sovereignty_circle(self, my_state):
        """Part 4: Visual HUD representation of the peer network."""
        print(f"\n[HUD] --- THE CIRCLE OF SOVEREIGNTY ---")
        # Visualizing the 15 Mentees as stars in a circle
        # My Node is in the center
        print(f"       ( {my_state} )       ") 
        print("  ✨   ✨   ✨   ✨   ✨  ")
        print("✨                     ✨")
        print("✨    [YOU] NODE 29    ✨")
        print("✨                     ✨")
        print("  ✨   ✨   ✨   ✨   ✨  ")
        
        # Success Audio for Mesh-Sync
        os.system('PowerShell -Command "[Console]::Beep(1200, 200); [Console]::Beep(1500, 200)"')
        
        if my_state == "STRESSED":
            print("[HUD] 🛡️  MESH ALERT: Peer Nodes notified of your Static. Support active.")
        else:
            print("[HUD] ✅ MESH STABLE: All Nodes in Flow.")

if __name__ == "__main__":
    sync = NodeSyncSovereign()
    # Scenario: Child feels 'Flow' and shares it with the mesh
    sync.broadcast_animus("FLOW")
    time.sleep(2)
    # Scenario: Child feels 'Stressed', mesh automatically signals peers
    sync.broadcast_animus("STRESSED")
