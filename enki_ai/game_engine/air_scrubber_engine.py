import math

class AirScrubberEngine:
    def calculate_centrifugal_force(self, velocity_ms, radius_mm):
        # Using the Law of Enlil to separate the 'Heavy Breath' from the 'Light'
        radius_m = radius_mm / 1000
        force = (velocity_ms**2) / radius_m
        print(f"\n[ATMOS] 🌪️  CALCULATING ENLIL CYCLONE FORCE...")
        print(f"[HUD] INTAKE VELOCITY: {velocity_ms} m/s")
        print(f"[HUD] SEPARATION FORCE: {force:.2f} m/s²")
        print("VERDICT: Toxins spun to the outer Graphene-shield. Air purified. OUSH.")

if __name__ == "__main__":
    AirScrubberEngine().calculate_centrifugal_force(15.5, 50)
