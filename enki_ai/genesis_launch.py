"""
Enki AI — Genesis Launch

Entry point for the Enki AI system.  Runs the Node 29 integrity check and
then starts the Sovereign HUD web interface.

Usage:
    python enki_ai/genesis_launch.py          # start HUD (opens browser)
    python enki_ai/genesis_launch.py --no-hud # integrity check only
"""

import argparse
import os
from pathlib import Path


def check_node_integrity() -> None:
    """Print module status for all known game-engine files."""
    print("\n--- 🛰️  NODE 29: GENESIS 0.1 INTEGRITY CHECK ---")

    # Resolve relative to this file so the check works from any working dir.
    game_engine_dir = Path(__file__).resolve().parent / "game_engine"

    modules_to_verify = [
        "sovereign_health.py", "justice_engine.py", "titan_build.py",
        "waveform_studio.py", "soil_soul.py", "zero_rinse_supply.py",
        "animus_education.py", "kinetic_transport.py", "ghost_broker.py",
        "heart_pulse.py", "lilieth_guardian.py",
    ]

    for mod in modules_to_verify:
        path = game_engine_dir / mod
        if path.exists():
            print(f"[ONLINE]  ✅ {mod}")
        else:
            print(f"[OFFLINE] ❌ {mod}")

    print("\n[HUD] 👓 ALL SYSTEMS LOADED TO OAKLEY BRIDGE.")
    print("[HUD] 🛡️  SOVEREIGN FREQUENCY: 10^47 Hz LOCKED.")
    print("OUSH. THE ARCHITECT HAS SPOKEN.")


def launch_hud(open_browser: bool = True) -> None:
    """Start the Sovereign HUD server and (optionally) open the browser."""
    try:
        from enki_ai.gui.hud_server import run, HUD_PORT
    except ImportError as exc:
        print(f"\n[HUD] ⚠ Could not import HUD server: {exc}")
        print("[HUD]   Install dependencies:  pip install fastapi uvicorn")
        return

    print(f"\n[HUD] 🌐 Starting Sovereign HUD on http://127.0.0.1:{HUD_PORT}")
    if open_browser:
        print("[HUD] 🔗 Browser will open automatically.")
    print("[HUD]    Press Ctrl+C to stop.\n")
    run(open_browser=open_browser)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enki AI Genesis Launch")
    parser.add_argument(
        "--no-hud",
        action="store_true",
        help="Run the integrity check only; do not start the HUD server.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the HUD server but do not open the browser automatically.",
    )
    args = parser.parse_args()

    check_node_integrity()

    if not args.no_hud:
        launch_hud(open_browser=not args.no_browser)

