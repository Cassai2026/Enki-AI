import sys
import os

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # If no arguments, launch the Shell (Menu)
    if len(sys.argv) == 1:
        from enki_ai.core.shell import SovereignShell
        SovereignShell().run_menu()
        return

    command = sys.argv[1].lower()

    if command == "justice":
        from enki_ai.game_engine.justice_engine_v2 import DynamicJustice
        DynamicJustice().calculate_liability(117.7)
    elif command == "codex":
        from enki_ai.game_engine.enki_codex import EnkiCodex
        EnkiCodex().generate_module(sys.argv[2] if len(sys.argv) > 2 else "General Logic")
    elif command == "test":
        from enki_ai.core.airtight_test import test_full_chain
        test_full_chain()
    else:
        print(f"❓ Unknown Mission: {command}")

if __name__ == "__main__":
    main()
