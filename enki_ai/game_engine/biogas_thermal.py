def monitor_dissociation_temp(current_temp):
    """Tracks the fire element for waste-to-ash conversion."""
    target = 750 # Sumerian Thermal Standard
    if current_temp < target:
        print(f"\n[FORGE] 🔥 Increasing thermal flux. Current: {current_temp}C | Target: {target}C")
    else:
        print(f"\n[FORGE] ✅ Molecular Dissociation Active. Producing Sovereign Ash.")
if __name__ == "__main__": monitor_dissociation_temp(745)
