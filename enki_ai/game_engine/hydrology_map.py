def overlay_drainage_grid(groundwater_lvl):
    """4D Overlay for Oakley HUD: Tracking the 50m Deep Stone Drainage."""
    print(f"\n[HUD] 🌊 OVERLAY ACTIVE: Stretford Water Table")
    print(f"[DATA] Groundwater Saturation: {groundwater_lvl}%")
    if groundwater_lvl > 85:
        print("[ALERT] 🏗️ Opening Section 20 Drainage Sluice to protect Primary School.")
    else:
        print("[HUD] ✅ Fertile Gradient Stable. The Stinking Ditch is now a Garden.")
if __name__ == "__main__": overlay_drainage_grid(78)
