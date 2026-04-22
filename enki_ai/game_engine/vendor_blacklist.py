import json

class VendorBlacklist:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/vendor_blacklist.json"

    def audit_vendor(self, vendor_name):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[SHIELD] 🛡️  AUDITING VENDOR FOR EXTRACTION RISK: {vendor_name}")
        
        for v in data['blacklist']:
            if v['name'] == vendor_name:
                print(f"🚩 ALERT: {vendor_name} is BLACKLISTED. Reason: {v['reason']}")
                return False
        print(f"✅ STATUS: {vendor_name} cleared for Sovereign Procurement.")
        return True

if __name__ == "__main__":
    VendorBlacklist().audit_vendor("Silly_Boy_Consulting_LTD")
