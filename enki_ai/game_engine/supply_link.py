import json
import os

class SupplyLinkSovereign:
    def __init__(self):
        # Ensure data directory exists
        if not os.path.exists("enki_ai/game_engine/data"):
            os.makedirs("enki_ai/game_engine/data")
        self.resource_ledger = "enki_ai/game_engine/data/resource_mesh.json"

    def audit_resource(self, item_name, quoted_price, raw_cost):
        """Part 1 & 3: Material Auditor with Fixed Float Specifiers."""
        markup = quoted_price - raw_cost
        markup_percent = (markup / raw_cost) * 100
        
        print(f"\n[SUPPLY] 📦 AUDITING: {item_name}")
        # Fixed: Changed :.2d to :.2f for currency precision
        print(f"[HUD] RAW COST: £{raw_cost:.2f} | QUOTED: £{quoted_price:.2f}")
        
        if markup_percent > 15:
            print(f"[HUD] 🚩 WARNING: 'Silly Boy' Margin Stacking detected ({markup_percent:.1f}%).")
            print("[HUD] ACTION: Search for Root Source or local Peer-Swap.")
            return "RINSE_DETECTED"
        else:
            print("[HUD] ✅ PRICE IS SOVEREIGN. Proceed with procurement.")
            return "PRICE_STABLE"

    def find_local_nodes(self):
        """Part 2: Mapping Resource Nodes in Stretford."""
        nodes = {
            "Stretford Mall Scrap": "Node_01_Recycle",
            "M32 Arches Graphene": "Node_07_Source",
            "Peer Node 15": "Surplus PET-G"
        }
        print("\n[HUD] 📍 NEAREST RESOURCE NODES:")
        for loc, resource in nodes.items():
            print(f"👉 {loc}: {resource}")

    def share_surplus(self, item):
        """Part 4: The Peer-to-Peer Exchange Ledger."""
        print(f"\n[MESH] 📡 BROADCASTING SURPLUS: {item}")
        entry = {"node": "NODE_29", "item": item, "status": "AVAILABLE"}
        with open(self.resource_ledger, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        os.system('PowerShell -Command "[Console]::Beep(1200, 200); [Console]::Beep(1800, 200)"')

if __name__ == "__main__":
    supply = SupplyLinkSovereign()
    # Scenario: Auditing Graphene Sheet with correct currency logic
    status = supply.audit_resource("Graphene Sheet", 150.50, 80.00)
    if status == "RINSE_DETECTED":
        supply.find_local_nodes()
        supply.share_surplus("Old Soldering Iron")
