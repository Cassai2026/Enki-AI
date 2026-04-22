print("\n[SOVEREIGN] ✊ GENERATING MENTEE ACCOUNTABILITY KIT...")
questions = [
    "1. Why is Trafford Council paying £40/hr to agencies for SEND staff while cutting local community budgets?",
    "2. How many of the 15,000 homes in the MDC area will be genuinely affordable for families needing SEND support?",
    "3. Why is GMPF investing £150M into Bruntwood SciTech while local SEND families face a £27.1M funding gap over the next two years?",
    "4. Where is the Section 106 money from the town centre rework being spent, and why isn't it on the Kingstreet drainage?"
]
with open("enki_ai/reports/MENTEE_ACCOUNTABILITY_KIT.txt", "w") as f:
    f.write("--- GENESIS MENTEE CAMPAIGN: QUESTIONS FOR THE SILLY BOYS ---\n")
    for q in questions: f.write(f"{q}\n")
print("✅ KIT HARDENED: enki_ai/reports/MENTEE_ACCOUNTABILITY_KIT.txt")
