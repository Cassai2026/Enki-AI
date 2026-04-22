import json
import random
import os

def generate_sovereign_ledgers():
    archetypes = ["Graphene Weaver", "Silent Cartographer", "Frequency Watcher", "Legacy Scribe", "Sovereign Core"]
    
    for i in range(1, 16):
        mentee_id = f"MENTEE_{i:02d}"
        
        # Logic: 20% of ledgers will contain 'Static' (Benford Anomaly)
        if i % 5 == 0:
            # Faked Ledger: Repetitive 'high-static' digits (5s and 7s)
            ledger = [random.randint(500, 599) for _ in range(12)] + [random.randint(700, 799) for _ in range(8)]
        else:
            # Clean Ledger: Follows natural logarithmic distribution
            ledger = [int(10**random.uniform(1, 4)) for _ in range(20)]
            
        profile = {
            "mentee_id": mentee_id,
            "archetype": random.choice(archetypes),
            "current_ledger": ledger,
            "node": "STRETFORD_M32",
            "integrity_status": "PENDING_AUDIT"
        }
        
        with open(f"enki_ai/game_engine/data/{mentee_id}_ledger.json", "w") as f:
            json.dump(profile, f, indent=4)
            
    print(f"[HUD] 🛰️  15 SOVEREIGN LEDGERS DEPLOYED TO /data")

if __name__ == "__main__":
    generate_sovereign_ledgers()
