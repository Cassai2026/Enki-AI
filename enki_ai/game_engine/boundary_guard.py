class BoundaryLayer:
    def __init__(self):
        self.rules = {
            "max_cognitive_load": 85,
            "human_agency_required": ["LEGAL", "MEDICAL", "FINANCIAL"],
            "grounding_trigger": "LOOP_DETECTED"
        }

    def check_intervention(self, current_state):
        """The 'Slow Down' Protocol."""
        if current_state['load'] > self.rules['max_cognitive_load']:
            return "ACTION: SILENCE_AND_REGULATE. Return agency to Human."
        if current_state['sector'] in self.rules['human_agency_required']:
            return "ACTION: ADVISE_ONLY. Human must execute."
        return "ACTION: PROCEED_WITH_SCAFFOLDING"
