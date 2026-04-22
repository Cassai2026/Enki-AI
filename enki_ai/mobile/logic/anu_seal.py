import hashlib
import time
import json
import os

class AnuMobileSeal:
    def __init__(self, mentee_id):
        self.mentee_id = mentee_id
        self.vault_path = "enki_ai/mobile/storage/vault"
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)

    def seal_evidence(self, category, observation, sensor_data=None):
        """
        Generates a cryptographically hashed evidence packet.
        Format: Category | Observation | Timestamp | Hash
        """
        timestamp = time.time()
        readable_time = time.ctime(timestamp)
        
        # Creating the unique fingerprint for this specific moment
        raw_string = f"{self.mentee_id}-{timestamp}-{category}-{observation}"
        fingerprint = hashlib.sha256(raw_string.encode()).hexdigest()
        
        packet = {
            "node_origin": f"TITAN_{self.mentee_id}",
            "timestamp": readable_time,
            "category": category,
            "observation": observation,
            "sensor_readings": sensor_data if sensor_data else "N/A",
            "evidence_fingerprint": fingerprint,
            "legal_standing": "CONTEMPORANEOUS_LOG"
        }
        
        # Save to the mobile vault
        filename = f"EVIDENCE_{int(timestamp)}.json"
        with open(os.path.join(self.vault_path, filename), 'w') as f:
            json.dump(packet, f, indent=4)
            
        print(f"\n[APP] 🛡️  EVIDENCE SEALED: {category}")
        print(f"[APP] 🔐 FINGERPRINT: {fingerprint[:16]}...")
        return packet

if __name__ == "__main__":
    # Test: Mentee 01 audits a structural hazard
    app = AnuMobileSeal(mentee_id="01")
    app.seal_evidence(
        category="STRUCTURAL_NEGLEGENCE", 
        observation="Exposed high-voltage wiring, Stretford Mall Walkway",
        sensor_data={"pm25": 12.5, "volt_detected": "LIVE"}
    )
