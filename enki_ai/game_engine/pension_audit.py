import json

class PensionAudit:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/scitech_specs.json"

    def audit_pension_leakage(self):
        print(f"\n[FORENSIC] 🏛️  AUDITING THE GMPF-BRUNTWOOD INTERLOCK...")
        
        gmpf_injection = 150000000
        council_bailout = 12640000
        
        ratio = gmpf_injection / council_bailout
        print(f"[HUD] GMPF CASH INTO BRUNTWOOD: £{gmpf_injection/1e6}M")
        print(f"[HUD] COUNCIL BAILOUT LOAN: £{council_bailout/1e6}M")
        print(f"[HUD] EXTRACTION RATIO: {ratio:.1f}x")
        print("VERDICT: The public pension fund is fueling private asset growth 11x faster than the Council can fund its own survival.")

if __name__ == "__main__":
    PensionAudit().audit_pension_leakage()
