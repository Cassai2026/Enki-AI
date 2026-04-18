import requests

class MerseyFlow:
    def __init__(self):
        # Station ID for River Mersey at Ashton Weir / Stretford area
        self.api_url = "https://environment.data.gov.uk/flood-monitoring/id/stations/690142/readings?_sorted&_limit=1"

    def scan_runoff(self):
        """Pulls live hydrology data from the Environment Agency API."""
        print("[HYDRO] 🌊 CONNECTING TO MERSEY NODE 01 (STRETFORD)...")
        try:
            response = requests.get(self.api_url, timeout=10)
            data = response.json()
            latest_level = data['items'][0]['value']
            
            status = "STABLE" if latest_level < 3.0 else "HIGH DISCHARGE"
            
            print(f"[HUD] LATEST RIVER LEVEL: {latest_level}m")
            return {
                "level": latest_level,
                "status": status,
                "frequency": "10^47_CLEAN"
            }
        except Exception as e:
            return "🌊 OFFLINE: Local Mesh Sync Required."

if __name__ == "__main__":
    mersey = MerseyFlow()
    print(mersey.scan_runoff())
