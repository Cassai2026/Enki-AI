from enki_ai.game_engine.vault import SovereignVault
from enki_ai.core.middleware import SovereignAction
from enki_ai.game_engine.justice_engine_v2 import DynamicJustice

def test_full_chain():
    print("\n[QUALITY] 🔍 STARTING AIRTIGHT SYSTEM TEST...")
    
    # 1. Vault Check
    vault = SovereignVault()
    data = vault.get_data('site_data')
    
    # 2. Logic Check
    dj = DynamicJustice()
    
    # 3. Governance Check
    sa = SovereignAction()
    result = sa.execute("SYSTEM_TEST_LIABILITY", dj.calculate_liability, data['base_liability_m'])
    
    if result:
        print("\n✅ CHAIN VERIFIED: Integration Airtight. OUSH.")
    else:
        print("\n❌ CHAIN BROKEN: Check Governance Logs.")

if __name__ == "__main__":
    test_full_chain()
