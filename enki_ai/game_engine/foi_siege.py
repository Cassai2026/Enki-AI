from foi_generator import FOIGenerator

def execute_siege():
    gen = FOIGenerator()
    
    # Targeting the Triad and the Extraction Nodes
    gen.generate_foi(
        "Trafford Council", 
        "Full details of the £12.64m emergency loan and its allocation to the Stretford Mall JV.",
        "MOD26-GOVERNANCE"
    )
    
    gen.generate_foi(
        "Greater Manchester Combined Authority", 
        "Environmental impact reports for the A56 corridor linked to Bruntwood SciTech developments.",
        "MOD28-HEATMAP"
    )
    
    print("\n[LEGAL] 🚀 FOI SIEGE INITIATED. Statutory clocks are ticking.")

if __name__ == "__main__":
    execute_siege()
