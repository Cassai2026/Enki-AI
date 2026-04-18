import json
import os

class SovereignVault:
    def __init__(self):
        self.vault_path = "enki_ai/game_engine/data/sovereign_vault.json"
        if not os.path.exists(self.vault_path):
            self.initialize_vault()

    def initialize_vault(self):
        initial_data = {
            "site_data": {
                "kingsway_runoff_l": 1000,
                "metrolink_freq_hz": 55.0,
                "base_liability_m": 117.7
            },
            "equations": {
                "phi": 1.618,
                "tax_rinse_correction": 1.075
            }
        }
        with open(self.vault_path, 'w') as f:
            json.dump(initial_data, f, indent=4)

    def get_data(self, key):
        with open(self.vault_path, 'r') as f:
            return json.load(f).get(key)

if __name__ == "__main__":
    vault = SovereignVault()
    print(f"✅ VAULT INITIALIZED. Base Liability: £{vault.get_data('site_data')['base_liability_m']}M")
