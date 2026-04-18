from ubo_scraper import UBOScraper
from ubo_matcher import UBOMatcher

def execute_unmasking():
    scraper = UBOScraper()
    matcher = UBOMatcher()
    
    scraper.scrape_psc_data("01234567") # The target shell ID
    if matcher.run_match():
        print("\n[LEGAL] ⚖️  UNMASKING COMPLETE: Corporate veil pierced.")
        print("[HUD] ACTION: Forwarding to Burton Copeland Litigation Team.")

if __name__ == "__main__":
    execute_unmasking()
