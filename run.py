import sys
import os

# Add the project root to the sys.path automatically
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def launch_justice():
    from enki_ai.game_engine.justice_engine_v2 import DynamicJustice
    justice = DynamicJustice()
    justice.calculate_liability(117.7)

if __name__ == "__main__":
    print("[BOOT] 🚀 ENKI AI KERNEL LOADING...")
    launch_justice()
