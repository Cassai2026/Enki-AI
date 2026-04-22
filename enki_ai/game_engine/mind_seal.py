import json

class MindSeal:
    def verify_membership(self, pulse_bpm, gesture_detected):
        print(f"\n[NEURAL] 🔒 INITIATING SOVEREIGN MIND-SEAL CHECK...")
        
        # Checking for the 'Architect Handshake' and a steady, calm pulse
        if gesture_detected == "SOVEREIGN_PINCH" and 60 <= pulse_bpm <= 100:
            print("[HUD] RESONANCE VERIFIED. ACCESS GRANTED.")
            print("[HUD] WELCOME TO THE MATRIX, INITIATE.")
            return True
        else:
            print("🚩 ACCESS DENIED: Frequency Mismatch. Membership Required.")
            return False

if __name__ == "__main__":
    MindSeal().verify_membership(72, "SOVEREIGN_PINCH")
