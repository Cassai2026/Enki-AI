import sys
import os

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Detect if we are in "Dev Mode" to stop the annoying menu
    if len(sys.argv) > 1 and sys.argv[1].lower() == "dev":
        print("[SOVEREIGN_OS] 🛠️  DEV_MODE ACTIVE. Shell Suspended.")
        return

    # If no arguments, launch the Shell (Menu)
    if len(sys.argv) == 1:
        from enki_ai.core.shell import SovereignShell
        SovereignShell().run_menu()
        return

    # Handle specific commands
    command = sys.argv[1].lower()
    if command == "justice":
        from enki_ai.game_engine.justice_engine_v2 import DynamicJustice
        DynamicJustice().calculate_liability(117.7)
    elif command == "test":
        from enki_ai.core.airtight_test import test_full_chain
        test_full_chain()
    else:
        print(f"❓ Unknown Mission: {command}")

if __name__ == "__main__":
    main()
