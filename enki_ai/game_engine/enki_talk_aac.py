import os
import time

class EnkiIntegratedTalk:
    def __init__(self):
        self.dwell_threshold = 1.5
        self.vibe = "STABLE"
        # Standard vocab for Flow state
        self.flow_vocab = {
            "HIGH": {"phrase": "Everything is in flow.", "icon": "⭐"},
            "MID": {"phrase": "I need a break.", "icon": "🌊"},
            "LOW": {"phrase": "Assistance required.", "icon": "🛡️"}
        }
        # Emergency vocab for Aggressive state
        self.shield_vocab = {
            "HIGH": {"phrase": "Please stop. I am uncomfortable.", "icon": "🛑"},
            "MID": {"phrase": "I am leaving this conversation now.", "icon": "🚪"},
            "LOW": {"phrase": "HELP. This person is aggressive.", "icon": "🆘"}
        }

    def update_social_context(self, label):
        """Sets the HUD state based on Social Clue Interceptor."""
        self.vibe = label
        if label == "AGGRESSIVE":
            print("[HUD] 🚨 SHIELD MODE ACTIVE: Vocab remapped for protection.")
        else:
            print(f"[HUD] ✅ VIBE: {label}. Flow state maintained.")

    def execute_comm(self, zone):
        """Executes speech while checking social context."""
        zone = zone.upper()
        # Choose vocab based on the vibe nudge
        active_vocab = self.shield_vocab if self.vibe == "AGGRESSIVE" else self.flow_vocab
        
        data = active_vocab[zone]
        print(f"\n[HUD] ✋ ZONE: {zone} | 🛡️  ACTIVE_VIBE: {self.vibe}")
        
        # Dwell simulation with visual warning if aggressive
        for i in range(1, 4):
            time.sleep(self.dwell_threshold / 3)
            prefix = "⚠️ SHIELDING" if self.vibe == "AGGRESSIVE" else "💎 SYNCING"
            print(f"[HUD] {prefix} {i*33}% ...")

        phrase = data["phrase"]
        os.system(f'PowerShell -Command "Add-Type –AssemblyName System.Speech; ' +
                  f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{phrase}\')"')
        return True

if __name__ == "__main__":
    talk = EnkiIntegratedTalk()
    
    # Scenario: Interceptor detects Aggression
    talk.update_social_context("AGGRESSIVE")
    # Child reaches 'HIGH' (Top zone) - normally OUSH, now it's a STOP command
    talk.execute_comm("HIGH")
