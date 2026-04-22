class SocialClueInterceptor:
    def __init__(self):
        self.current_vibe = "STABLE"

    def analyze_social_dynamic(self, db_level, pitch_variation, sentiment_score):
        """Differentiates between 'Loudness' and 'Aggression'."""
        
        # LOGIC: Aggression usually has high volume + low pitch variation + negative sentiment
        # Loudness is just high volume + high pitch variation + neutral/positive sentiment
        
        print("\n[SOCIAL] 🛰️  INTERCEPTING CONVERSATION DYNAMICS...")
        
        if db_level > 80:
            if pitch_variation > 0.5 and sentiment_score >= 0:
                nudge = "📢 NOTICE: User is just being LOUD / EXCITED. No threat detected."
                label = "LOUD_FRIENDLY"
            elif pitch_variation < 0.3 and sentiment_score < 0:
                nudge = "⚠️ ALERT: Aggressive tone detected. Maintain Somatic Shield."
                label = "AGGRESSIVE"
            else:
                nudge = "📢 NOTICE: High volume environment. Minimal threat."
                label = "LOUD_STATIC"
        else:
            nudge = "💎 CRYSTAL: Conversation is stable."
            label = "STABLE"

        print(f"[HUD] NUDGE: {nudge}")
        return label

if __name__ == "__main__":
    nudge_sys = SocialClueInterceptor()
    
    # Scenario: Someone is shouting happily at a football match or M32 Hub
    print("--- Test: Loud but Friendly ---")
    nudge_sys.analyze_social_dynamic(db_level=85, pitch_variation=0.7, sentiment_score=0.5)
    
    # Scenario: Someone is being aggressive in a meeting
    print("\n--- Test: Truly Aggressive ---")
    nudge_sys.analyze_social_dynamic(db_level=85, pitch_variation=0.1, sentiment_score=-0.8)
