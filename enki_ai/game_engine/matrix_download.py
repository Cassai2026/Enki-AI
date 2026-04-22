import json

class MatrixDownload:
    def __init__(self):
        # The Skill-Tree Mapping
        self.library = {
            "DAMAGED_BRICKWORK": "Module_156_Sovereign_Masonry",
            "EXPOSED_WIRING": "Module_212_Industrial_Sparky",
            "LEGAL_NOTICE": "Module_130_Sovereign_Law",
            "SOIL_CONTAMINATION": "Module_126_Graphene_Bio"
        }

    def initiate_upload(self, detected_object):
        print(f"\n[NEURAL] 👁️  SCANNING OBJECT: {detected_object}...")
        
        if detected_object in self.library:
            skill_node = self.library[detected_object]
            print(f"[HUD] 📥 DOWNLOADING: {skill_node}...")
            print(f"[HUD] STATUS: Uploading logic gates to Smart Glasses...")
            print("VERDICT: Knowledge Seated. You now know how to fix this. OUSH.")
        else:
            print("[HUD] UNKNOWN OBJECT: Searching Global Mesh for new Animus Instructions.")

if __name__ == "__main__":
    MatrixDownload().initiate_upload("DAMAGED_BRICKWORK")
