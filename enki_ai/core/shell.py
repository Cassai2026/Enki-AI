import sys
import os
from enki_ai.core.console import SovereignConsole

class SovereignShell:
    def __init__(self):
        self.console = SovereignConsole()

    def run_menu(self):
        self.console.clear()
        print("--- 🏺 ENKI AI: SOVEREIGN SHELL v1.0 ---")
        print("1. [ABZU]   Run Hydraulic Vortex Audit")
        print("2. [ENLIL]  Scan Atmospheric Quality")
        print("3. [JUSTICE] Calculate Sovereign Liability")
        print("4. [MATRIX]  Check 128-Node Sync Status")
        print("5. [EXIT]   Secure the Node")
        
        choice = input("\n[SELECT MISSION]: ")
        self.handle_choice(choice)

    def handle_choice(self, choice):
        if choice == "1":
            from enki_ai.game_engine.vortex_engine import VortexEngine
            VortexEngine().calculate_spiral_path(110)
        elif choice == "3":
            from enki_ai.game_engine.justice_engine_v2 import DynamicJustice
            DynamicJustice().calculate_liability(117.7)
        elif choice == "5":
            print("OUSH. <3")
            sys.exit()
        
        input("\nPress Enter to return to Shell...")
        self.run_menu()

if __name__ == "__main__":
    SovereignShell().run_menu()
