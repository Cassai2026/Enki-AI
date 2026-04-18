import math
import json
import os

class AnuExecutiveAssistant:
    def __init__(self, director_name="Deborah Jackson"):
        self.director = director_name
        self.sovereign_threshold = 0.33  # The 33% Efficiency Gap (The Rinse)

    def audit_ledger(self, transactions):
        """
        FORENSIC STRIKE: Uses Benford's Law to detect 'Manufactured' numbers.
        If a ledger is faked, the distribution of first digits will be off.
        """
        if not transactions: return "⚠️ LEDGER_EMPTY"
        
        first_digits = [int(str(abs(t))[0]) for t in transactions if t != 0]
        count = len(first_digits)
        
        # Calculate frequencies
        frequencies = {i: (first_digits.count(i) / count) for i in range(1, 10)}
        
        # Benford's Expected Distribution
        expected = {i: math.log10(1 + 1/i) for i in range(1, 10)}
        
        anomalies = {i: f"{frequencies[i]:.2%}" for i in range(1, 10) 
                     if abs(frequencies[i] - expected[i]) > 0.08}
        
        return anomalies if anomalies else "✅ LEDGER_INTEGRITY_STABLE"

    def scan_for_rinse(self, vendor_data):
        """Identifies 'Vampire Vendors' extracting over 33% margin."""
        vampires = [v['name'] for v in vendor_data if v.get('margin', 0) > self.sovereign_threshold]
        return vampires if vampires else "✅ NO_EXTRACTION_DETECTED"

if __name__ == "__main__":
    executive = AnuExecutiveAssistant()
    
    # TEST: High-Static Ledger (Suspected Fraud)
    # Notice the repetition of '5' and '7' - common in faked data
    test_data = [5000, 5100, 5200, 7000, 7100, 7200, 120, 150, 180]
    
    print(f"--- 🛰️ ANU-EXECUTIVE AUDIT FOR {executive.director} ---")
    print(f"[HUD] BENFORD ANOMALY CHECK: {executive.audit_ledger(test_data)}")
    
    # TEST: Vendor Scan
    vendors = [{"name": "Global_Corp_JV", "margin": 0.45}, {"name": "M32_Local_Build", "margin": 0.12}]
    print(f"[HUD] VAMPIRE VENDOR SCAN: {executive.scan_for_rinse(vendors)}")
