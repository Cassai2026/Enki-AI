"""
Tests for Enki AI Governance Law (enki_ai.core.governance).
"""

import pytest

from enki_ai.core.governance import (
    LAWS,
    LAWS_BY_ID,
    LAW_ADAPTIVE_SUPPORT,
    LAW_BIAS_AUDIT,
    LAW_DATA_MINIMISATION,
    LAW_DIMENSIONAL_INFERENCE,
    LAW_EDGE_CASE_INCLUSION,
    LAW_HUMAN_OVERSIGHT,
    LAW_NO_REPLACEMENT,
    LAW_NO_SILENT_PROFILING,
    LAW_STABILITY_PRIORITY,
    LAW_TRANSPARENCY,
    DecisionRecord,
    GovernanceEngine,
    GovernanceViolation,
    Law,
    engine,
)


# ---------------------------------------------------------------------------
# Law registry
# ---------------------------------------------------------------------------


def test_ten_laws_defined():
    assert len(LAWS) == 10


def test_law_ids_unique():
    ids = [law.id for law in LAWS]
    assert len(ids) == len(set(ids))


def test_laws_by_id_covers_all():
    assert set(LAWS_BY_ID.keys()) == {law.id for law in LAWS}


def test_each_law_has_principle_and_plain_english():
    for law in LAWS:
        assert law.principle.strip(), f"{law.id} missing principle"
        assert law.plain_english.strip(), f"{law.id} missing plain_english"


def test_law_is_frozen():
    with pytest.raises((AttributeError, TypeError)):
        LAW_HUMAN_OVERSIGHT.name = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GovernanceEngine – check_action / is_permitted
# ---------------------------------------------------------------------------


class TestCheckAction:
    def setup_method(self):
        self.eng = GovernanceEngine()

    # L02 – Human Oversight

    def test_recommend_without_human_review_violates_L02(self):
        violations = self.eng.check_action("recommend_support")
        assert LAW_HUMAN_OVERSIGHT in violations

    def test_recommend_with_human_review_clears_L02(self):
        violations = self.eng.check_action(
            "recommend_support", context={"human_reviewed": True}
        )
        assert LAW_HUMAN_OVERSIGHT not in violations

    def test_allocate_without_human_review_violates_L02(self):
        violations = self.eng.check_action("allocate_resource")
        assert LAW_HUMAN_OVERSIGHT in violations

    # L03 – No Silent Profiling

    def test_collect_without_consent_violates_L03(self):
        violations = self.eng.check_action("collect_data")
        assert LAW_NO_SILENT_PROFILING in violations

    def test_collect_with_consent_clears_L03(self):
        violations = self.eng.check_action(
            "collect_data", context={"consent_given": True}
        )
        assert LAW_NO_SILENT_PROFILING not in violations

    def test_profile_without_consent_violates_L03(self):
        violations = self.eng.check_action("profile_user")
        assert LAW_NO_SILENT_PROFILING in violations

    # L07 – No Replacement

    def test_replaces_human_flag_violates_L07(self):
        violations = self.eng.check_action(
            "respond_to_learner", context={"replaces_human": True}
        )
        assert LAW_NO_REPLACEMENT in violations

    def test_without_replaces_human_flag_clears_L07(self):
        violations = self.eng.check_action(
            "respond_to_learner", context={"replaces_human": False}
        )
        assert LAW_NO_REPLACEMENT not in violations

    # Compliant action

    def test_neutral_action_no_violations(self):
        violations = self.eng.check_action("play_sound")
        assert violations == []

    def test_is_permitted_true_for_clean_action(self):
        assert self.eng.is_permitted("play_sound") is True

    def test_is_permitted_false_for_violating_action(self):
        assert self.eng.is_permitted("recommend_support") is False


# ---------------------------------------------------------------------------
# GovernanceEngine – assert_permitted
# ---------------------------------------------------------------------------


class TestAssertPermitted:
    def setup_method(self):
        self.eng = GovernanceEngine()

    def test_assert_permitted_raises_on_violation(self):
        with pytest.raises(GovernanceViolation) as exc_info:
            self.eng.assert_permitted("recommend_support")
        assert "L02" in str(exc_info.value)

    def test_assert_permitted_passes_clean_action(self):
        self.eng.assert_permitted("play_sound")  # should not raise

    def test_governance_violation_carries_violated_laws(self):
        try:
            self.eng.assert_permitted("recommend_support")
        except GovernanceViolation as exc:
            assert LAW_HUMAN_OVERSIGHT in exc.violated_laws
            assert exc.action == "recommend_support"

    def test_governance_violation_message_contains_law_id(self):
        with pytest.raises(GovernanceViolation, match="L02"):
            self.eng.assert_permitted("allocate_resource")


# ---------------------------------------------------------------------------
# GovernanceEngine – audit log / log_decision
# ---------------------------------------------------------------------------


class TestAuditLog:
    def setup_method(self):
        self.eng = GovernanceEngine()

    def test_log_decision_adds_to_audit_log(self):
        self.eng.log_decision("play_sound", rationale="user requested")
        assert len(self.eng.audit_log()) == 1

    def test_log_decision_returns_decision_record(self):
        record = self.eng.log_decision("play_sound", rationale="user requested")
        assert isinstance(record, DecisionRecord)

    def test_decision_record_fields(self):
        record = self.eng.log_decision(
            "suggest_resource",
            rationale="attention index < 0.4",
            human_reviewed=True,
            context={"lsv_attention": 0.3},
        )
        assert record.action == "suggest_resource"
        assert record.rationale == "attention index < 0.4"
        assert record.human_reviewed is True
        assert record.context["lsv_attention"] == 0.3
        assert record.timestamp  # non-empty ISO timestamp

    def test_audit_log_returns_copy(self):
        self.eng.log_decision("a", rationale="r1")
        log_copy = self.eng.audit_log()
        log_copy.clear()
        assert len(self.eng.audit_log()) == 1  # original unchanged

    def test_clear_audit_log(self):
        self.eng.log_decision("a", rationale="r1")
        self.eng.clear_audit_log()
        assert self.eng.audit_log() == []

    def test_multiple_decisions_accumulated(self):
        for i in range(5):
            self.eng.log_decision(f"action_{i}", rationale=f"reason {i}")
        assert len(self.eng.audit_log()) == 5


# ---------------------------------------------------------------------------
# GovernanceEngine – human override
# ---------------------------------------------------------------------------


class TestHumanOverride:
    def setup_method(self):
        self.eng = GovernanceEngine()

    def test_require_human_override_logs_record(self):
        self.eng.require_human_override("recommend_support")
        log = self.eng.audit_log()
        assert len(log) == 1
        assert log[0].human_reviewed is True
        assert log[0].context.get("override") is True

    def test_require_human_override_records_action(self):
        self.eng.require_human_override("allocate_resource")
        assert self.eng.audit_log()[0].action == "allocate_resource"


# ---------------------------------------------------------------------------
# GovernanceEngine – summarise
# ---------------------------------------------------------------------------


def test_summarise_contains_all_law_ids():
    summary = GovernanceEngine.summarise()
    for law in LAWS:
        assert law.id in summary
        assert law.name in summary


def test_summarise_contains_plain_english():
    summary = GovernanceEngine.summarise()
    # Spot-check one plain-english line
    assert "The computer suggests" in summary


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_module_engine_is_governance_engine():
    assert isinstance(engine, GovernanceEngine)
