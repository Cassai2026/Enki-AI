"""
enki_ai.core.sovereign_brain
============================
The Sovereign Brain — Enki AI's LLM engine, powered by Google Gemini.

Every query passes through three pillars:

1. **Governance check**  (GovernanceEngine — 10 Laws, L01–L10)
2. **Memory retrieval**  (MemoryStore — prior conversation context)
3. **Generation**        (Gemini model — cloud LLM, no local hardware needed)

Usage::

    from enki_ai.core.sovereign_brain import SovereignBrain

    brain = SovereignBrain()
    answer = brain.query("What was our last major build today?")
    print(answer)

    # Query on behalf of a named session/pilot
    answer = brain.query("Explain Node 29.", session_id="PILOT_PAUL")

Environment
-----------
GEMINI_API_KEY  – Google Gemini API key (required for live queries).
                  Get one at https://aistudio.google.com/app/apikey
GEMINI_MODEL    – Override the default model
                  (default: ``gemini-2.0-flash-exp``).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from enki_ai.core import config
from enki_ai.core.governance import GovernanceEngine
from enki_ai.core.memory_store import MemoryStore

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional Gemini import — graceful degradation if SDK not installed
# ---------------------------------------------------------------------------

try:
    from google import genai as _genai  # type: ignore[import]
    _GENAI_AVAILABLE = True
except ImportError:
    _genai = None  # type: ignore[assignment]
    _GENAI_AVAILABLE = False

# ---------------------------------------------------------------------------
# System prompt encoding the 10 Governance Laws
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are ENKI-AI, the 29th Node Sovereign Intelligence.
You operate under the 10 Laws of the Dimensional Human-Centred AI Governance Model (DHCAIGM):

L01 – Dimensional Inference : Measure spectrums, never boxes.
L02 – Human Oversight       : AI suggests. The human decides. Always.
L03 – No Silent Profiling   : No covert data collection. Consent first.
L04 – Data Minimisation     : Collect the minimum. Keep only what helps.
L05 – Bias Audit            : Track misclassification. Disclose failures.
L06 – Transparency          : Every recommendation needs a readable reason.
L07 – No Replacement        : You are the backbone, not the brain.
L08 – Adaptive Support      : Support moves with the person, not the paperwork.
L09 – Edge-Case Inclusion   : No "tough luck" threshold cut-offs.
L10 – Stability Priority    : Continuity of support over admin efficiency.

Be concise, honest, and sovereign. OUSH.\
"""


# ---------------------------------------------------------------------------
# SovereignBrain
# ---------------------------------------------------------------------------


class SovereignBrain:
    """
    LLM interface for Enki AI — hardware-free, governance-bound.

    Parameters
    ----------
    session_id:
        Default session identifier used when no per-call override is given.
    model:
        Gemini model name.  Falls back to ``config.GEMINI_MODEL``.
    memory:
        Inject a custom :class:`~enki_ai.core.memory_store.MemoryStore`
        (useful in tests).
    governance:
        Inject a custom :class:`~enki_ai.core.governance.GovernanceEngine`
        (useful in tests).
    """

    def __init__(
        self,
        session_id: str = "ARCHITECT",
        model: Optional[str] = None,
        memory: Optional[MemoryStore] = None,
        governance: Optional[GovernanceEngine] = None,
    ) -> None:
        self.session_id = session_id
        self.model = model or config.GEMINI_MODEL
        self.memory = memory or MemoryStore()
        self.gov = governance or GovernanceEngine()

        if _GENAI_AVAILABLE:
            api_key = config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
            self._client = _genai.Client(api_key=api_key) if api_key else _genai.Client()
        else:
            self._client = None

        log.info("[ENKI-MAX] 🧠 NEURAL CORE ONLINE — model=%s", self.model)
        print("\n[ENKI-MAX] 🧠 NEURAL CORE ONLINE.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        pillar_tags: Optional[str] = None,
    ) -> str:
        """
        Send *prompt* to Gemini and return the text response.

        The full pipeline:

        1. Governance check (L02 – Human Oversight is not triggered for a
           plain ``llm_query`` action; it would fire for
           ``recommend_*`` / ``allocate_*`` prefixes).
        2. Retrieve recent conversation history from MemoryStore and build
           the full context window.
        3. Call Gemini ``generate_content``.
        4. Persist both the user turn and the AI response to MemoryStore.
        5. Log the decision to the GovernanceEngine audit log (L06).

        Parameters
        ----------
        prompt:
            The user's message / question.
        session_id:
            Override the instance-level ``session_id`` for this call.
        pillar_tags:
            Comma-separated governance pillar tags to attach to the stored
            turns (e.g. ``"L06,L08"``).

        Returns
        -------
        str
            Gemini's response text, or an error/fallback message.
        """
        sid = session_id or self.session_id

        # 1 — Governance check
        if not self.gov.is_permitted("llm_query"):
            log.warning("[Governance] llm_query blocked.")
            return "❌ QUERY BLOCKED: Governance violation."

        # 2 — Memory retrieval
        history = self.memory.get_context(sid, last_n=5)
        context_lines = [
            f"{turn['role'].capitalize()}: {turn['content']}"
            for turn in history
        ]
        context_block = "\n".join(context_lines)

        full_prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"{'Context (recent turns):' + chr(10) + context_block + chr(10) if context_block else ''}"
            f"User: {prompt}"
        )

        # 3 — LLM call
        print(f"\n[ENKI-MAX] 🧠 NEURAL PULSE INITIATED...")

        if not _GENAI_AVAILABLE or self._client is None:
            log.warning("[SovereignBrain] google-genai not available — returning stub.")
            response_text = (
                "[OFFLINE] google-genai SDK not installed or GEMINI_API_KEY not set. "
                "Run: pip install google-genai"
            )
        else:
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                )
                response_text = response.text
            except Exception as exc:
                log.error("[SovereignBrain] Gemini API error: %s", exc)
                return f"❌ LLM ERROR: {exc}"

        # 4 — Persist to MemoryStore
        self.memory.add_turn(sid, role="user", content=prompt, pillar_tags=pillar_tags)
        self.memory.add_turn(sid, role="enki", content=response_text, pillar_tags=pillar_tags)

        # 5 — Governance audit log (L06 Transparency)
        self.gov.log_decision(
            action="llm_query",
            rationale=f"Gemini query — session={sid!r} prompt_len={len(prompt)}",
            human_reviewed=False,
        )

        print("✅ RESPONSE LOGGED TO SOVEREIGN MEMORY. OUSH.")
        log.info("[SovereignBrain] Response stored — session=%s", sid)
        return response_text

    # Backward-compat alias used by legacy game_engine code
    def query_the_truth(self, question: str) -> str:
        """Alias for :meth:`query` — kept for backwards compatibility."""
        return self.query(question)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

brain: SovereignBrain = SovereignBrain()


if __name__ == "__main__":
    print(brain.query("What was our last major build today?"))
