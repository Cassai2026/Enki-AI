import math

class TitanBuildSimulator:
    def __init__(self):
        # Material Constants (Titan-Spec)
        self.graphene_pet_tensile = 150.0  # GPa (Hardened PET)
        self.copper_rubber_conductivity = 10**8 # S/m (Shielding)
        self.safety_factor = 1.5 # 150% Hardened

    def calculate_tetrahedron_load(self, side_length, material_type):
        """
        Calculates the structural integrity of the Double Pyramid Node.
        Logic: Surface Area vs. Telluric Pressure.
        """
        # Area of a regular tetrahedron = sqrt(3) * a^2
        surface_area = math.sqrt(3) * (side_length**2)
        
        # Load capacity based on material strength
        if material_type == "Graphene-PET":
            capacity = surface_area * self.graphene_pet_tensile
        else:
            capacity = surface_area * 50.0 # Standard 'Static' material
            
        final_rating = capacity / self.safety_factor

        print(f"\n[ENGINEERING] 🏗️  STRUCTURAL SCAN: Dual-Tetrahedron Node")
        print(f"[HUD] MATERIAL: {material_type}")
        print(f"[HUD] SURFACE AREA: {surface_area:.2f} m²")
        print(f"[HUD] LOAD CAPACITY: {final_rating:.2f} kN (150% Hardened)")
        
        if material_type == "Graphene-PET":
            print("[HUD] ✅ STATUS: TITAN-SPEC. Ready for Lightning-Harvesting.")
        else:
            print("[WARNING] ❌ STATUS: STATIC-GRADE. Structural failure imminent under Ion-Pulsing.")

if __name__ == "__main__":
    simulator = TitanBuildSimulator()
    # Testing the 10m side-length Biodome shell
    simulator.calculate_tetrahedron_load(10, "Graphene-PET")
