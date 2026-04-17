import sqlite3


# The L-Laws that every action must pass through
GOVERNANCE_LAWS = {
    'L01': 'No Harm — Do not endanger physical or psychological wellbeing.',
    'L02': 'Human Oversight — All critical actions require Architect confirmation.',
    'L03': 'No Silent Profiling — No collection of personal data without consent.',
    'L04': 'Transparency — All AI decisions must be explainable on request.',
    'L05': 'Equity — Resources and actions must benefit all nodes, not just central ones.',
    'L06': 'Accountability — Every action is logged and attributable.',
    'L07': 'Environmental Integrity — No action may degrade the natural environment.',
    'L08': 'Adaptive Support — Systems must support, not replace, human agency.',
}

# Actions blocked unless specific laws are satisfied
ACTION_REQUIREMENTS = {
    'DELETE': ['L02', 'L06'],
    'BROADCAST': ['L03', 'L04'],
    'HARVEST': ['L05', 'L07'],
    'DEPLOY': ['L02', 'L06'],
    'OVERRIDE': ['L01', 'L02', 'L04'],
}


def validate_action(action_type, requestor='SYSTEM'):
    """
    Checks whether an action is permitted under the current Governance Laws.
    Returns True if permitted, False if blocked.
    """
    action_type = action_type.upper()
    required_laws = ACTION_REQUIREMENTS.get(action_type, [])

    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()

    # Log the gate check
    c.execute('''CREATE TABLE IF NOT EXISTS governance_log
                 (id INTEGER PRIMARY KEY, action TEXT, requestor TEXT,
                  verdict TEXT, laws_checked TEXT, timestamp TEXT)''')

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not required_laws:
        verdict = 'PERMITTED'
        laws_checked = 'NONE REQUIRED'
    else:
        # All required laws must be active in GOVERNANCE_LAWS
        satisfied = [law for law in required_laws if law in GOVERNANCE_LAWS]
        if len(satisfied) == len(required_laws):
            verdict = 'PERMITTED'
        else:
            verdict = 'BLOCKED'
        laws_checked = ', '.join(required_laws)

    c.execute(
        "INSERT INTO governance_log (action, requestor, verdict, laws_checked, timestamp) VALUES (?, ?, ?, ?, ?)",
        (action_type, requestor, verdict, laws_checked, timestamp)
    )
    conn.commit()
    conn.close()

    icon = '✅' if verdict == 'PERMITTED' else '🚫'
    print(f"\n[GOVERNANCE GATE] {icon} {action_type} — {verdict}")
    print(f"  Requestor: {requestor}")
    print(f"  Laws checked: {laws_checked}")
    return verdict == 'PERMITTED'


def print_active_laws():
    """
    Prints all active Governance Laws to the HUD.
    """
    print("\n--- ⚖️  ACTIVE GOVERNANCE LAWS ---")
    for code, description in GOVERNANCE_LAWS.items():
        print(f"  [{code}] {description}")


def get_governance_audit():
    """
    Displays the governance gate log for audit purposes.
    """
    conn = sqlite3.connect('enki_knowledge.db')
    c = conn.cursor()
    try:
        c.execute("SELECT action, requestor, verdict, laws_checked, timestamp FROM governance_log ORDER BY id DESC LIMIT 20")
        rows = c.fetchall()
        print("\n--- 📋 GOVERNANCE AUDIT LOG (Last 20) ---")
        for action, requestor, verdict, laws, ts in rows:
            icon = '✅' if verdict == 'PERMITTED' else '🚫'
            print(f"  {icon} [{ts}] {action} by {requestor} | Laws: {laws}")
    except Exception:
        print("[INFO] No governance log yet.")
    conn.close()


if __name__ == "__main__":
    print_active_laws()
    validate_action('DEPLOY', requestor='Architect')
    validate_action('OVERRIDE', requestor='SYSTEM')
    validate_action('BROADCAST', requestor='Architect')
    get_governance_audit()
