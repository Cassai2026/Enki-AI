import json
import os

class SovereignIdentityMatrix:
    def __init__(self):
        self.matrix_file = "enki_ai/game_engine/data/identity_matrix.json"
        if not os.path.exists("enki_ai/game_engine/data"):
            os.makedirs("enki_ai/game_engine/data")
        self.archetypes = self._load_archetypes()

    def _load_archetypes(self):
        # The 15 predefined Titan archetypes
        return {
            "01": {"name": "Graphene Weaver", "color": "Gold", "voice": "Calm", "icon": "💎"},
            "02": {"name": "Silent Cartographer", "color": "Blue", "voice": "Soft", "icon": "🧭"},
            "03": {"name": "Frequency Watcher", "color": "Red", "voice": "Sharp", "icon": "🛡️"},
            # ... (Full 15 would be loaded here)
            "15": {"name": "Sovereign Core", "color": "Rainbow", "voice": "Oden", "icon": "OUSH"}
        }

    def assign_mentee_avatar(self, mentee_id, archetype_id):
        """Part 1: The Identity Assignment."""
        if archetype_id in self.archetypes:
            arch = self.archetypes[archetype_id]
            profile = {
                "mentee_id": mentee_id,
                "archetype": arch["name"],
                "hud_color": arch["color"],
                "voice_synth": arch["voice"],
                "success_icon": arch["icon"]
            }
            
            print(f"\n[IDENTITY] 👤 ASSIGNING AVATAR TO MENTEE {mentee_id}...")
            print(f"[HUD] ARCHETYPE: {profile['archetype']}")
            print(f"[HUD] TONE: {profile['hud_color']} | ICON: {profile['success_icon']}")
            
            # Part 4: The Biological Ledger (Local Storage)
            self._save_profile(profile)
            return profile
        else:
            print("[IDENTITY] 🚩 ERROR: Invalid Archetype ID.")
            return None

    def _save_profile(self, profile):
        # Each mentee gets their own local profile file
        file_path = f"enki_ai/game_engine/data/mentee_{profile['mentee_id']}_profile.json"
        with open(file_path, 'w') as f:
            json.dump(profile, f)
        print(f"[LEDGER] ✅ Profile saved locally: {file_path}")

if __name__ == "__main__":
    matrix = SovereignIdentityMatrix()
    # Scenario: Assigning the 'Graphene Weaver' (01) avatar to Mentee 01
    matrix.assign_mentee_avatar(mentee_id="01", archetype_id="01")
