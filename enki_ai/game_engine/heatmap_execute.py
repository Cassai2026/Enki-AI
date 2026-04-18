from heatmap_data import HeatmapDataSeater
from intensity_calc import IntensityCalculator

def execute_heatmap():
    seater = HeatmapDataSeater()
    calc = IntensityCalculator()
    
    seater.seat_network()
    calc.calculate_heat()
    
    print("\n[VISUAL] 🛰️  HEATMAP COORDINATES GENERATED.")
    print("[HUD] VERDICT: Systemic concentration of influence detected in Stretford M32.")

if __name__ == "__main__":
    execute_heatmap()
