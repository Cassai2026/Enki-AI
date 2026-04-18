class SomaticAudio:
    def __init__(self):
        self.threshold_low = 65
        self.threshold_high = 100
        self.current_mode = "TRANSPARENT"

    def auto_mute(self, current_bpm):
        """Adjusts the acoustic environment based on Somatic State."""
        print(f"\n[SOMATIC] ❤️ HEART RATE DETECTED: {current_bpm} BPM")
        
        if current_bpm > self.threshold_high:
            self.current_mode = "ISOLATION"
            action = "🚫 BLOCKING EXTERNAL STATIC | ACTIVATING 432Hz BINAURAL SHIELD"
        elif current_bpm < self.threshold_low:
            self.current_mode = "FLOW"
            action = "🎵 ZEN-STATE: ACTIVATING AMBIENT RECOVERY TRACKS"
        else:
            self.current_mode = "TRANSPARENT"
            action = "👂 PASS-THROUGH ACTIVE: WORLD IS STABLE"
            
        print(f"[HUD] MODE: {self.current_mode}")
        return action

if __name__ == "__main__":
    audio = SomaticAudio()
    # Simulating a high-stress "Administrative Sloth" encounter
    print(audio.auto_mute(110))
