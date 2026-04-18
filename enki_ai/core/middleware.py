from enki_ai.core.governance import GovernanceEngine

class SovereignAction:
    """Wrapper to ensure every trade/engineering action hits the Law first."""
    def __init__(self):
        self.gov = GovernanceEngine()

    def execute(self, action_name, logic_func, *args, **kwargs):
        print(f"\n[GOVERNANCE] 🛡️  AUDITING ACTION: {action_name}")
        # Check against the 10 Laws (L01-L10)
        if self.gov.is_permitted(action_name):
            print(f"✅ LAWFUL. Executing...")
            return logic_func(*args, **kwargs)
        else:
            print(f"❌ VIOLATION. Action {action_name} blocked by Sovereign Law.")
            return None

if __name__ == "__main__":
    from enki_ai.game_engine.justice_engine_v2 import DynamicJustice
    dj = DynamicJustice()
    sa = SovereignAction()
    sa.execute("CALCULATE_LIABILITY", dj.calculate_liability, 117.7)
