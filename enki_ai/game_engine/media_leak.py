import json

class MediaLeak:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/media_leak_specs.json"

    def generate_press_release(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[BROADCAST] 📣 GENERATING SOVEREIGN PRESS PACKET...")
        
        release = f"HEADLINE: {data['headline']}\n"
        release += f"FORENSIC DATA: £{data['stats']['Total_Debt']:,} Municipal Debt.\n"
        release += f"BIOLOGICAL THEFT: {data['stats']['Tree_Loss_Years']} years of canopy destroyed.\n"
        release += "SOURCE: The 29th Node Sovereign Audit.\n"
        
        with open("enki_ai/reports/PRESS_LEAK_PACKET.txt", "w") as f: f.write(release)
        print("✅ PACKET HARDENED. READY FOR MESH BROADCAST.")

if __name__ == "__main__":
    MediaLeak().generate_press_release()
