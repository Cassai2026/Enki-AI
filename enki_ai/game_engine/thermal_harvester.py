class ThermalHarvester:
    def calculate_yield(self, tarmac_temp, drain_temp):
        delta_t = tarmac_temp - drain_temp
        wattage_per_sqm = delta_t * 0.15 # Theoretical TEG efficiency
        print(f"\n[ENERGY] 🔥 HARVESTING TARMAC THERMAL DIFFERENTIAL...")
        print(f"[HUD] TEMP DELTA: {delta_t}°C")
        print(f"[HUD] SOVEREIGN WATTS GENERATED: {wattage_per_sqm:.2f}W/m²")
        return "Powering Mesh Node..."

if __name__ == "__main__":
    ThermalHarvester().calculate_yield(48.5, 14.2)
