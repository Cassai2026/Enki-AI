import json

class DataSanitizer:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/scrub_specs.json"

    def sanitize_for_uplink(self, raw_text):
        with open(self.spec_file, 'r') as f: specs = json.load(f)
        print(f"\n[SECURITY] 🧼 SANITIZING DATA FOR GLOBAL UPLINK...")
        
        sanitized = raw_text
        for word in specs['scrub_list']:
            sanitized = sanitized.replace(word, specs['replacement'])
            
        print("✅ STATUS: Privacy Mask Applied. Ready for Genesis Bridge.")
        return sanitized

if __name__ == "__main__":
    print(DataSanitizer().sanitize_for_uplink("Cass needs to sue Tom Ross in Stretford."))
