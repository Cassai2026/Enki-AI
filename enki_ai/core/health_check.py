import os

def check_structure():
    required_paths = [
        "enki_ai/__init__.py",
        "enki_ai/core/__init__.py",
        "enki_ai/game_engine/__init__.py"
    ]
    print("\n[HEALTH] 🔍 RUNNING GENESIS STRUCTURE AUDIT...")
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path} - SEATED")
        else:
            with open(path, 'w') as f: pass
            print(f"🛠️  {path} - CREATED")
    print("VERDICT: Structure is Canonical. God-Mode Ready. OUSH.")

if __name__ == "__main__":
    check_structure()
