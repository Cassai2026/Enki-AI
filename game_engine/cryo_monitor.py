def check_thermal_exchange(block_temp, ambient_temp):
    """Monitors recycled Antarctic ice-melt cooling for data cores."""
    delta = block_temp - ambient_temp
    print(f"\n[CRYO] 🧊 H4O EXCHANGE STATUS: {delta}K Delta")
    if block_temp > 273:  # Threshold
        print("[WARNING] ❌ Thermal Bleed detected. Increasing Ice-Sled flow.")
    else:
        print("[HUD] ✅ Super-Conductive state maintained at 10^47 frequency.")


if __name__ == "__main__":
    check_thermal_exchange(270, 290)
