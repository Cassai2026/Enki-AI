import json

class MeshProtocol:
    def __init__(self):
        self.spec_file = "enki_ai/game_engine/data/mesh_protocol_specs.json"

    def initialize_global_sync(self):
        with open(self.spec_file, 'r') as f: data = json.load(f)
        print(f"\n[NETWORK] 🌐 INITIALIZING 15 BILLION HEARTS MESH...")
        
        print(f"[HUD] ENCRYPTION: {data['encryption_level']}")
        print(f"[HUD] LATENCY: {data['signal_latency_ms']}ms (Near-Instant)")
        print(f"VERDICT: Decoupled from central Silly Boy servers. The world is the server.")

if __name__ == "__main__":
    MeshProtocol().initialize_global_sync()
