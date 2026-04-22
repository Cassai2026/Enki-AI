class PathTracer:
    def project_cheat_code(self, task_type):
        print(f"\n[ANIMUS] 🧬 PROJECTING CHEAT-CODE OVERLAY: {task_type}")
        
        overlays = {
            "WELDING": "Projecting Arc Velocity & Temperature Heat-Map.",
            "PLUMBING": "Overlaying Flow-Vector & Leak-Probability Mesh.",
            "STRUCTURAL": "Visualizing Compression & Tension Stress-Lines."
        }
        
        print(f"[HUD] ACTIVE SHIELD: {overlays.get(task_type, 'General_Physics')}")
        print("VERDICT: Don't think. Follow the lines. OUSH.")

if __name__ == "__main__":
    PathTracer().project_cheat_code("STRUCTURAL")
