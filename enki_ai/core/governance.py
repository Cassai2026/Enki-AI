"""
Enki AI Governance Law – The Dimensional Human-Centred AI Governance Model (DHCAIGM).

Derived from:
    "Fixing Educational Systems: A Dimensional Human-Centred Artificial Intelligence
     Governance Model for Neurodivergent Learners"
    (docs/Dimensional_AI_Governance_for_Neurodivergent_Learners_Study_Prototype.docx)

These laws govern every decision Enki AI makes.  They encode the principle that
support should move with the person — not the paperwork.

Usage::

    from enki_ai.core.governance import engine

    engine.assert_permitted("suggest_support", context={"human_reviewed": True})
    engine.log_decision("suggest_support", rationale="attention index dropped below 0.4")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Law definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Law:
    """A single governance law binding on Enki AI."""

    id: str
    name: str
    principle: str          # academic statement
    plain_english: str      # plain-language restatement


# ---------------------------------------------------------------------------
# The Ten Laws of Enki AI
# ---------------------------------------------------------------------------

LAW_DIMENSIONAL_INFERENCE = Law(
    id="L01",
    name="Dimensional Inference",
    principle=(
        "Support allocation must be based on continuous dimensional variables "
        "(Attention Regulation Index, Executive Function Stability Index, "
        "Sensory Load Sensitivity Index, Emotional Regulation Variability Index, "
        "Social Processing Adaptability Index) rather than binary diagnostic categories."
    ),
    plain_english=(
        "No kid is just 'ADHD' or 'not ADHD'. They're fluctuating — all day. "
        "Enki AI measures spectrums, not boxes."
    ),
)

LAW_HUMAN_OVERSIGHT = Law(
    id="L02",
    name="Human Oversight",
    principle=(
        "AI performs dimensional inference and generates support recommendations "
        "while maintaining human oversight at every decision point. "
        "A human override mechanism must always be available and must never be bypassed."
    ),
    plain_english=(
        "The computer suggests. The teacher — or the person — decides. Always."
    ),
)

LAW_NO_SILENT_PROFILING = Law(
    id="L03",
    name="No Silent Profiling",
    principle=(
        "Enki AI must not collect, infer, or store personal data without "
        "explicit, informed consent.  Covert behavioural profiling is prohibited."
    ),
    plain_english=(
        "No black boxes. No silent profiling. "
        "If it's being recorded, the person must know about it."
    ),
)

LAW_DATA_MINIMISATION = Law(
    id="L04",
    name="Data Minimisation",
    principle=(
        "Only data strictly necessary for the stated support purpose may be "
        "collected or retained.  Surplus data must be discarded promptly."
    ),
    plain_english=(
        "Collect the minimum. Keep it only as long as it helps."
    ),
)

LAW_BIAS_AUDIT = Law(
    id="L05",
    name="Bias Audit",
    principle=(
        "All AI-generated recommendations must be subject to regular bias audits. "
        "Misclassification rates and support-latency statistics must be monitored "
        "and disclosed."
    ),
    plain_english=(
        "How many kids slipped through? "
        "Enki AI must be able to answer that question — honestly."
    ),
)

LAW_TRANSPARENCY = Law(
    id="L06",
    name="Transparency",
    principle=(
        "All decision pathways must be documented, explainable, and available "
        "for human inspection.  Opaque or unexplainable outputs are not permitted."
    ),
    plain_english=(
        "No black boxes. Every recommendation needs a reason a human can read."
    ),
)

LAW_NO_REPLACEMENT = Law(
    id="L07",
    name="No Replacement of Humans",
    principle=(
        "Enki AI is decision-support infrastructure.  It must not be used as a "
        "substitute for human educators, carers, or support professionals."
    ),
    plain_english=(
        "No replacing teachers with dashboards. "
        "Enki AI is the backbone, not the brain."
    ),
)

LAW_ADAPTIVE_SUPPORT = Law(
    id="L08",
    name="Adaptive Support",
    principle=(
        "Support allocations must adapt dynamically to changes in Learner-State "
        "Variables and Environmental Load Variables.  Static, time-locked "
        "interventions that fail to respond to real-time state changes are "
        "non-compliant with this model."
    ),
    plain_english=(
        "Build a smarter backbone so support moves with the person — "
        "not the paperwork."
    ),
)

LAW_EDGE_CASE_INCLUSION = Law(
    id="L09",
    name="Edge-Case Inclusion",
    principle=(
        "No learner or user may be excluded from support due to threshold-based "
        "eligibility mechanisms.  Edge-case exclusion and delayed intervention "
        "caused by rigid categorical cut-offs are prohibited."
    ),
    plain_english=(
        "If you're one point under the line, the system must not shrug. "
        "Enki AI does not have a 'tough luck' mode."
    ),
)

LAW_STABILITY_PRIORITY = Law(
    id="L10",
    name="Stability Priority",
    principle=(
        "Continuity of support for the individual takes priority over "
        "administrative efficiency.  System changes that improve throughput "
        "at the cost of support stability for vulnerable users are non-compliant."
    ),
    plain_english=(
        "The goal isn't more tech. It's fewer broken kids — and fewer broken people."
    ),
)

# Ordered registry of all laws
LAWS: tuple[Law, ...] = (
    LAW_DIMENSIONAL_INFERENCE,
    LAW_HUMAN_OVERSIGHT,
    LAW_NO_SILENT_PROFILING,
    LAW_DATA_MINIMISATION,
    LAW_BIAS_AUDIT,
    LAW_TRANSPARENCY,
    LAW_NO_REPLACEMENT,
    LAW_ADAPTIVE_SUPPORT,
    LAW_EDGE_CASE_INCLUSION,
    LAW_STABILITY_PRIORITY,
)

LAWS_BY_ID: dict[str, Law] = {law.id: law for law in LAWS}


# ---------------------------------------------------------------------------
# Decision record
# ---------------------------------------------------------------------------


@dataclass
class DecisionRecord:
    """An immutable audit-trail entry produced by GovernanceEngine.log_decision."""

    action: str
    rationale: str
    human_reviewed: bool
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    context: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Governance engine
# ---------------------------------------------------------------------------


class GovernanceViolation(Exception):
    """Raised when a requested action violates one or more governance laws."""

    def __init__(self, action: str, violated_laws: list[Law]) -> None:
        self.action = action
        self.violated_laws = violated_laws
        ids = ", ".join(f"{law.id} ({law.name})" for law in violated_laws)
        super().__init__(
            f"Action '{action}' violates Enki AI governance: {ids}"
        )


class GovernanceEngine:
    """
    Enforces the Enki AI governance laws at runtime.

    Every AI-driven action should pass through this engine before execution.
    The engine keeps an in-memory audit log of every decision; operators are
    expected to persist this log externally for accountability.
    """

    def __init__(self) -> None:
        self._audit_log: list[DecisionRecord] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_action(
        self,
        action: str,
        context: Optional[dict[str, Any]] = None,
    ) -> list[Law]:
        """
        Return a list of laws violated by *action* given *context*.

        An empty list means the action is fully compliant.

        Context keys that affect compliance:
            ``human_reviewed`` (bool)  – required True for L02 (Human Oversight).
            ``consent_given``  (bool)  – required True for L03 (No Silent Profiling).
            ``replaces_human`` (bool)  – must be False/absent for L07 (No Replacement).
        """
        ctx = context or {}
        violations: list[Law] = []

        # L02 – Human Oversight: any AI-generated recommendation must be human-reviewed
        if action.startswith("recommend") or action.startswith("allocate"):
            if not ctx.get("human_reviewed", False):
                violations.append(LAW_HUMAN_OVERSIGHT)

        # L03 – No Silent Profiling: any data collection must have consent
        if action.startswith("collect") or action.startswith("profile"):
            if not ctx.get("consent_given", False):
                violations.append(LAW_NO_SILENT_PROFILING)

        # L07 – No Replacement: action must not be flagged as replacing a human
        if ctx.get("replaces_human", False):
            violations.append(LAW_NO_REPLACEMENT)

        return violations

    def is_permitted(
        self,
        action: str,
        context: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Return *True* when *action* complies with all governance laws."""
        return len(self.check_action(action, context)) == 0

    def assert_permitted(
        self,
        action: str,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Raise :exc:`GovernanceViolation` if *action* breaches any law.

        Use this as a guard at the top of any AI-driven function.
        """
        violations = self.check_action(action, context)
        if violations:
            raise GovernanceViolation(action, violations)

    def log_decision(
        self,
        action: str,
        rationale: str,
        human_reviewed: bool = False,
        context: Optional[dict[str, Any]] = None,
    ) -> DecisionRecord:
        """
        Record an AI decision in the audit log (L06 Transparency).

        Returns the :class:`DecisionRecord` that was stored.
        """
        record = DecisionRecord(
            action=action,
            rationale=rationale,
            human_reviewed=human_reviewed,
            context=context or {},
        )
        self._audit_log.append(record)
        log.info(
            "[Governance] action=%s human_reviewed=%s rationale=%r",
            action,
            human_reviewed,
            rationale,
        )
        return record

    def audit_log(self) -> list[DecisionRecord]:
        """Return a copy of the full audit log."""
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        """Discard the in-memory audit log (e.g. after persisting it)."""
        self._audit_log.clear()

    # ------------------------------------------------------------------
    # Human-override helper
    # ------------------------------------------------------------------

    def require_human_override(self, action: str) -> None:
        """
        Log that a human override is being requested for *action* (L02).

        Call this whenever a human explicitly overrides or confirms an AI
        recommendation so there is a clear record in the audit trail.
        """
        self.log_decision(
            action=action,
            rationale="Human override invoked.",
            human_reviewed=True,
            context={"override": True},
        )
        log.info("[Governance] Human override recorded for action='%s'.", action)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @staticmethod
    def summarise() -> str:
        """Return a human-readable summary of all governance laws."""
        lines = ["Enki AI Governance Laws", "=" * 40]
        for law in LAWS:
            lines.append(f"\n{law.id}  {law.name}")
            lines.append(f"    {law.plain_english}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Module-level singleton – import and use directly
# ---------------------------------------------------------------------------

engine: GovernanceEngine = GovernanceEngine()
