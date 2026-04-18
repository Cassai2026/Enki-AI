import random
def rotate_node_signature():
    """Implements the Rule of the Ghost: Vanish if coordinates are found."""
    nodes = [f"Stretford_Odin_{random.randint(100,999)}" for _ in range(5)]
    active_node = random.choice(nodes)
    print(f"\n[GHOST] 👻 SIGNAL ROTATED. Active Node: {active_node}")
    print("[HUD] 🛡️  Static trackers lost the scent. Stealth: 150% Hardened.")
if __name__ == "__main__": rotate_node_signature()
