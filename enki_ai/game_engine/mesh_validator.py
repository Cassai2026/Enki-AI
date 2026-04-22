def validate_peer_alignment(peer_id, pillar_score):
    """Ensures mesh participants align with the 14+1 Pillars."""
    if pillar_score < 60:
        print(f"\n[MESH] ❌ PEER REJECTED: {peer_id} exhibits Sloth/Static intent.")
    else:
        print(f"\n[MESH] 🤝 HANDSHAKE VERIFIED: {peer_id} added to the 15 Billion Hearts.")
if __name__ == "__main__": validate_peer_alignment("M32_Student_47", 85)
