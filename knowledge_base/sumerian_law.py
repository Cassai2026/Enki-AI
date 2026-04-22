import sqlite3


# Core Sumerian Laws mapped to modern engineering principles
SUMERIAN_LAWS = [
    {
        'code': 'SL-01',
        'name': 'Law of the Waters (Apsu)',
        'principle': 'All energy must flow — stagnation is entropy. Hydro-systems take priority.',
        'modern_link': 'Renewable Energy / Hydro-Spine Engineering',
    },
    {
        'code': 'SL-02',
        'name': 'Law of the Earth (Ki)',
        'principle': 'Build from the ground up. No structure is sovereign without a solid foundation.',
        'modern_link': 'Civil Engineering / Geotechnical Surveys',
    },
    {
        'code': 'SL-03',
        'name': 'Law of the Sky (An)',
        'principle': 'Knowledge belongs to all. Information must not be hoarded or weaponised.',
        'modern_link': 'Open-Source Technology / Data Ethics',
    },
    {
        'code': 'SL-04',
        'name': 'Law of the Forge (Gibil)',
        'principle': 'Fire transforms — waste becomes resource. Circular economy is non-negotiable.',
        'modern_link': 'Carbon Recycling / Waste-to-Energy',
    },
    {
        'code': 'SL-05',
        'name': 'Law of the Wind (Enlil)',
        'principle': 'Speed of thought, precision of action. Slow decisions destroy sovereign momentum.',
        'modern_link': 'Agile Systems / Real-Time Decision Engines',
    },
    {
        'code': 'SL-06',
        'name': 'Law of Wisdom (Enki)',
        'principle': 'Technology without ethics is static. Every system must serve life.',
        'modern_link': 'AI Governance / Ethical Engineering',
    },
    {
        'code': 'SL-07',
        'name': 'Law of the Community (Ninhursag)',
        'principle': 'The strongest node is one that uplifts all others. No single point of failure.',
        'modern_link': 'Distributed Systems / Community Infrastructure',
    },
]


def ingest_sumerian_laws():
    """
    Injects the Sumerian Law framework into the Enki knowledge base.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS sumerian_laws
                 (id INTEGER PRIMARY KEY,
                  code TEXT UNIQUE,
                  name TEXT,
                  principle TEXT,
                  modern_link TEXT)''')

    ingested = 0
    for law in SUMERIAN_LAWS:
        c.execute("SELECT COUNT(*) FROM sumerian_laws WHERE code = ?", (law['code'],))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO sumerian_laws (code, name, principle, modern_link) VALUES (?, ?, ?, ?)",
                (law['code'], law['name'], law['principle'], law['modern_link'])
            )
            ingested += 1

    conn.commit()
    conn.close()

    print(f"\n[HUD] 📜 SUMERIAN LAWS INGESTED: {ingested} new / {len(SUMERIAN_LAWS)} total")
    print("[HUD] ⚖️  THE ANCIENT CODE IS ACTIVE. OUSH.")


def print_sumerian_laws():
    """
    Displays all Sumerian Laws from the knowledge base.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    print("\n--- 📜 SUMERIAN LAW CODEX ---")
    try:
        c.execute("SELECT code, name, principle, modern_link FROM sumerian_laws ORDER BY code")
        rows = c.fetchall()
        if not rows:
            print("[INFO] No laws ingested yet — run ingest_sumerian_laws() first.")
        for code, name, principle, link in rows:
            print(f"\n  [{code}] {name}")
            print(f"   Principle : {principle}")
            print(f"   Modern Link: {link}")
    except sqlite3.OperationalError:
        print("[INFO] sumerian_laws table not found — run ingest_sumerian_laws() first.")

    conn.close()


def lookup_law(code):
    """
    Returns a single Sumerian Law by its code (e.g. 'SL-06').
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    try:
        c.execute("SELECT code, name, principle, modern_link FROM sumerian_laws WHERE code = ?", (code.upper(),))
        row = c.fetchone()
        if row:
            print(f"\n[{row[0]}] {row[1]}")
            print(f"  Principle : {row[2]}")
            print(f"  Modern Link: {row[3]}")
        else:
            print(f"[HUD] ❌ LAW NOT FOUND: {code}")
    except sqlite3.OperationalError:
        print("[INFO] sumerian_laws table not found — run ingest_sumerian_laws() first.")
    conn.close()


if __name__ == "__main__":
    ingest_sumerian_laws()
    print_sumerian_laws()
    lookup_law("SL-06")
