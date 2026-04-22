class SupplyAuditor:
    def __init__(self):
        # Estimated margin layers in traditional procurement
        self.waste_layers = {
            "Main_Contractor_Markup": 0.05,
            "Subcontractor_Margin": 0.12,
            "Procurement_Latency": 0.03
        }

    def check_stacking(self, quoted_price, material_name="Raw Materials"):
        """Identifies hidden 'Rinse' in a supply quote."""
        total_waste_pct = sum(self.waste_layers.values())
        true_value = quoted_price * (1 - total_waste_pct)
        margin_stack = quoted_price - true_value
        
        print(f"\n[SUPPLY] 📦 AUDITING QUOTE: {material_name}")
        print(f"[HUD] QUOTED PRICE: £{quoted_price:,.2f}")
        print(f"[HUD] HIDDEN MARGIN STACKING: £{margin_stack:,.2f}")
        print(f"[HUD] 🎯 TITAN-SPEC TRUE COST: £{true_value:,.2f}")
        
        if margin_stack > (quoted_price * 0.15):
            return "🚩 WARNING: EXCESSIVE RINSE DETECTED. REDIRECT TO ROOT SOURCE."
        return "✅ QUOTE WITHIN SOVEREIGN LIMITS."

if __name__ == "__main__":
    auditor = SupplyAuditor()
    # Testing a £10,000 material quote for Stretford Mall rewilding
    print(auditor.check_stacking(10000, "PET-Graphene Panels"))
