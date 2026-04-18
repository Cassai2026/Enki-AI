import time
import os

class EnkiVisualTimer:
    def __init__(self):
        self.buffer_active = False

    def start_sovereign_session(self, minutes, task_name="M32 Task"):
        """Visualizes time as a depleting spatial asset."""
        total_seconds = int(minutes * 60)
        warning_threshold = total_seconds * 0.2
        
        print(f"\n[CLOCK] ⏳ SESSION START: {task_name}")
        print(f"[HUD] DURATION: {minutes}m")

        for remaining in range(total_seconds, -1, -1):
            percent = (remaining / total_seconds) * 100
            
            # Transition Logic: Change HUD color based on time left
            status = "💎 FLOW"
            if remaining <= warning_threshold:
                status = "⚠️ TRANSITION"
                # Soft nudge sound every 10 seconds in warning phase
                if remaining % 10 == 0 and remaining > 0:
                    os.system('PowerShell -Command "[Console]::Beep(800, 100)"')

            # Visual HUD Bar
            bar_length = 40
            filled = int(bar_length * (remaining / total_seconds))
            bar = "█" * filled + "░" * (bar_length - filled)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"--- {task_name} ---")
            print(f"STATUS: {status}")
            print(f"TIME: {remaining//60:02d}:{remaining%60:02d}")
            print(f"[{bar}] {percent:.1f}%")
            
            time.sleep(1)

        self._signal_completion()

    def _signal_completion(self):
        """Final transition signal for the Animus."""
        print("\n[HUD] ✅ TRANSITION COMPLETE. READY FOR NEXT NODE.")
        # Harmonic completion tone
        os.system('PowerShell -Command "[Console]::Beep(1000, 500); [Console]::Beep(1200, 500)"')
        os.system('PowerShell -Command "Add-Type –AssemblyName System.Speech; ' +
                  f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'Task complete. Well done.\')"')

if __name__ == "__main__":
    clock = EnkiVisualTimer()
    # Test: 30-second Micro-Session for the Mentees
    clock.start_sovereign_session(0.5, "Node Synchronization")
