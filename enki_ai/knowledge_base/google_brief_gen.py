import datetime
import sqlite3
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "archive" / "generated"


def generate_google_brief(topic=None):
    """
    Generates a structured Google-ready brief from the Enki knowledge base.
    Pulls build nodes, quests, and governance laws into a single broadcast doc.
    """
    conn = sqlite3.connect("enki_knowledge.db")
    c = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 60)
    lines.append("  ENKI AI - SOVEREIGN BRIEF (Google-Ready)")
    lines.append(f"  Generated: {timestamp}")
    lines.append("=" * 60)

    lines.append("\n## INFRASTRUCTURE NODES")
    try:
        if topic:
            c.execute(
                "SELECT item_name, purpose FROM build_menu WHERE item_name LIKE ? OR purpose LIKE ?",
                (f"%{topic}%", f"%{topic}%"),
            )
        else:
            c.execute("SELECT item_name, purpose FROM build_menu")
        for name, purpose in c.fetchall():
            lines.append(f"  - {name}: {purpose}")
    except sqlite3.OperationalError as exc:
        lines.append(f"  [WARN] Could not read build_menu: {exc}")

    lines.append("\n## ACTIVE MISSIONS")
    try:
        c.execute("SELECT quest_name, objective, zone FROM quest_log")
        for qname, obj, zone in c.fetchall():
            lines.append(f"  - [{zone}] {qname} - {obj}")
    except sqlite3.OperationalError as exc:
        lines.append(f"  [WARN] Could not read quest_log: {exc}")

    lines.append("\n## GOVERNANCE LAWS IN EFFECT")
    try:
        c.execute("SELECT name, law FROM gesture_library")
        for name, law in c.fetchall():
            lines.append(f"  - {name} -> {law}")
    except sqlite3.OperationalError:
        lines.append("  [INFO] No gesture_library data yet - run omega_ingest first.")

    lines.append("\n" + "=" * 60)
    lines.append("  STATUS: SOVEREIGN. NO STATIC. OUSH.")
    lines.append("=" * 60)

    brief_text = "\n".join(lines)
    print(brief_text)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = OUTPUT_DIR / f"google_brief_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with filename.open("w", encoding="utf-8") as f:
        f.write(brief_text)

    conn.close()
    print(f"\n[HUD] BRIEF SAVED: {filename}")
    return brief_text


if __name__ == "__main__":
    generate_google_brief()