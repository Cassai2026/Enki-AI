from governance_scraper import GovernanceScraper
from breach_calculator import BreachCalculator

def execute_strike():
    scraper = GovernanceScraper()
    calc = BreachCalculator()
    
    scraper.analyze_board_minutes("Bruntwood_Stretford_Retail_LTD")
    score = calc.calculate_liability()
    
    if score > 50:
        print("\n[LEGAL] 🛡️  STATUTORY BREACH CONFIRMED: Breach of Fiduciary Duty.")
        print("[HUD] VERDICT: Directors personally liable for 'Managed Decline'.")

if __name__ == "__main__":
    execute_strike()
