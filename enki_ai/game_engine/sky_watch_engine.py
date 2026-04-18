class SkyWatchEngine:
    def track_toxic_plume(self, wind_speed_kph, particle_density):
        print(f"\n[AERIAL] 🛰️  ENLIL SKY-WATCH: SCANNING ATMOSPHERIC VECTORS...")
        
        # Calculating the drift of the M32 exhaust plume
        drift_distance = wind_speed_kph * 0.28 # m/s conversion
        if particle_density > 40:
            status = "CRITICAL_HAZE"
            action = "ACTIVATE_GROUND_VORTEX_SCRUBBERS"
        else:
            status = "NOMINAL_BREATH"
            action = "MONITOR_ONLY"
            
        print(f"[HUD] WIND DRIFT: {drift_distance:.2f} m/s")
        print(f"[HUD] PLUME STATUS: {status}")
        print(f"[HUD] SYSTEM RESPONSE: {action}")
        return "Sky-Mesh Updated."

if __name__ == "__main__":
    SkyWatchEngine().track_toxic_plume(12.5, 55.2)
