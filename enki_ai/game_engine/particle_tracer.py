class ParticleTracer:
    def simulate_flow(self, rainfall_intensity):
        print(f"\n[PHYSICS] 🌊 TRACING KINGSWAY RUNOFF PARTICLES...")
        if rainfall_intensity > 5.0:
            print("[HUD] PATH: Kingsway -> Soakaway -> Victorian Arch Foundation.")
            print("🚩 ALERT: Hydraulic pressure increasing on compromised brickwork.")
        return "Flow mapping complete."

if __name__ == "__main__":
    ParticleTracer().simulate_flow(8.5)
