import os
import platform

class SovereignConsole:
    @staticmethod
    def clear():
        command = "cls" if platform.system() == "Windows" else "clear"
        os.system(command)

    @staticmethod
    def notify(message):
        print(f"[SOVEREIGN_OS] {message}")
        # Add platform-specific desktop notifications here if needed

if __name__ == "__main__":
    SovereignConsole.clear()
    SovereignConsole.notify("System Cleaned and Synced.")
