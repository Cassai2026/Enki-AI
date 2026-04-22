class SkillCert:
    def verify_time_served(self, years_on_site, projects_completed):
        print("\n[CREDENTIALS] 📜 AUDITING TIME-SERVED EXPERIENCE...")
        if years_on_site > 10:
            print(f"[HUD] TOTAL EXPERIENCE: {years_on_site} Years.")
            print(f"[HUD] PRACTICAL MASTERY: Confirmed.")
            print("VERDICT: Issuing Sovereign Engineer Status. Degree redundant.")
        return "Sovereign Certificate Hardened."

if __name__ == "__main__":
    print(SkillCert().verify_time_served(22, 145))
