import subprocess

def set_system_volume(level: int):
    # Convert the level (0-100) to 0-65535 range for nircmd
    subprocess.run(f"nircmd.exe setsysvolume {level * 65535 // 100}")
    print(f"Volume set to {level}%")

# Test: Set volume to 50%
set_system_volume(50)