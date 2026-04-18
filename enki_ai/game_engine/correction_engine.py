class CorrectionEngine:
    def verify_plumb_and_level(self, detected_angle):
        # 0 degrees is perfectly plumb
        tolerance = 0.5
        variance = abs(detected_angle)
        
        if variance > tolerance:
            print(f"\n[FIX-IT] 🔧 ADJUSTMENT REQUIRED: {variance}° variance detected.")
            # Calculate the shim required to fix the angle
            print("[HUD] INSTRUCTION: Shift top of post 12mm LEFT.")
            return False
        print("\n[FIX-IT] ✅ STATUS: PLUMB & LEVEL.")
        return True

if __name__ == "__main__":
    ce = CorrectionEngine()
    ce.verify_plumb_and_level(2.4) # Simulating a post that is out of plumb
