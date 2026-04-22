"""
Tests for enki_ai.core.sovereign_brain (SovereignBrain).

Live Gemini calls are skipped automatically when google-genai is not
installed or GEMINI_API_KEY is not set, matching the project's convention
for optional-dependency tests.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from enki_ai.core.memory_store import MemoryStore
from enki_ai.core.governance import GovernanceEngine

# ---------------------------------------------------------------------------
# Conditional import — skip live tests gracefully
# ---------------------------------------------------------------------------

try:
    from google import genai as _genai  # type: ignore[import]
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

_LIVE_KEY = bool(os.environ.get("GEMINI_API_KEY"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_memory(tmp_path):
    """Isolated MemoryStore backed by a temp SQLite DB."""
    return MemoryStore(db_path=tmp_path / "test_brain.db", max_turns=50)


@pytest.fixture
def brain_offline(tmp_memory):
    """
    SovereignBrain with the Gemini client patched out so no network calls
    are made.  The mock returns a fixed response string.
    """
    from enki_ai.core.sovereign_brain import SovereignBrain

    gov = GovernanceEngine()
    b = SovereignBrain(session_id="TEST_PILOT", memory=tmp_memory, governance=gov)

    # Patch the internal client to avoid any real HTTP calls
    mock_response = MagicMock()
    mock_response.text = "SOVEREIGN VERDICT: Node 29 confirmed. OUSH."
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    b._client = mock_client

    return b


# ---------------------------------------------------------------------------
# Import / construction
# ---------------------------------------------------------------------------


def test_import():
    from enki_ai.core.sovereign_brain import SovereignBrain  # noqa: F401


def test_module_singleton():
    from enki_ai.core.sovereign_brain import brain, SovereignBrain
    assert isinstance(brain, SovereignBrain)


def test_construction(tmp_memory):
    from enki_ai.core.sovereign_brain import SovereignBrain
    b = SovereignBrain(session_id="PILOT_X", memory=tmp_memory)
    assert b.session_id == "PILOT_X"
    assert b.memory is tmp_memory


# ---------------------------------------------------------------------------
# query — with mocked Gemini client
# ---------------------------------------------------------------------------


def test_query_returns_string(brain_offline):
    result = brain_offline.query("What is Node 29?")
    assert isinstance(result, str)
    assert len(result) > 0


def test_query_stores_user_turn(brain_offline):
    brain_offline.query("Tell me about the Mersey drainage.")
    turns = brain_offline.memory.get_context("TEST_PILOT")
    roles = [t["role"] for t in turns]
    assert "user" in roles


def test_query_stores_enki_turn(brain_offline):
    brain_offline.query("Explain the Sovereign Equation.")
    turns = brain_offline.memory.get_context("TEST_PILOT")
    roles = [t["role"] for t in turns]
    assert "enki" in roles


def test_query_content_matches_response(brain_offline):
    result = brain_offline.query("Audit Trafford Council.")
    enki_turns = [
        t for t in brain_offline.memory.get_context("TEST_PILOT")
        if t["role"] == "enki"
    ]
    assert any(t["content"] == result for t in enki_turns)


def test_query_logs_decision_in_audit_log(brain_offline):
    brain_offline.query("Run governance check.")
    log = brain_offline.gov.audit_log()
    actions = [e.action for e in log]
    assert "llm_query" in actions


def test_query_session_override(brain_offline):
    brain_offline.query("Session override test.", session_id="OTHER_SESSION")
    turns = brain_offline.memory.get_context("OTHER_SESSION")
    assert len(turns) == 2  # user + enki


def test_query_context_window_grows(brain_offline):
    for i in range(3):
        brain_offline.query(f"Question {i}")
    turns = brain_offline.memory.get_context("TEST_PILOT")
    # 3 rounds × 2 turns each = 6
    assert len(turns) == 6


def test_query_includes_history_in_prompt(brain_offline):
    import enki_ai.core.sovereign_brain as _sb

    # Force the SDK-available flag so the mock client actually gets called
    original = _sb._GENAI_AVAILABLE
    try:
        _sb._GENAI_AVAILABLE = True
        # First round — populates memory with a specific, recognisable phrase
        brain_offline.query("Tell me about the Sovereign Equation")
        # Second round — the prompt fed to Gemini should contain the first turn
        brain_offline.query("Follow-up question")
    finally:
        _sb._GENAI_AVAILABLE = original

    calls = brain_offline._client.models.generate_content.call_args_list
    assert len(calls) >= 2, "Expected at least 2 Gemini calls"
    # The second call's prompt must contain the content of the first user message
    second_prompt = calls[1].kwargs.get("contents") or calls[1].args[0]
    assert "Sovereign Equation" in second_prompt


# ---------------------------------------------------------------------------
# Pillar tags
# ---------------------------------------------------------------------------


def test_query_stores_pillar_tags(brain_offline):
    brain_offline.query("Justice query.", pillar_tags="L06,L09")
    turns = brain_offline.memory.get_context("TEST_PILOT")
    assert any(t.get("pillar_tags") == "L06,L09" for t in turns)


# ---------------------------------------------------------------------------
# query_the_truth (backward-compat alias)
# ---------------------------------------------------------------------------


def test_query_the_truth_alias(brain_offline):
    result = brain_offline.query_the_truth("Who owns the Kingsway runoff?")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Offline / SDK-missing behaviour
# ---------------------------------------------------------------------------


def test_offline_fallback_message(tmp_memory):
    """When google-genai is absent, query() returns a helpful offline message."""
    from enki_ai.core.sovereign_brain import SovereignBrain

    b = SovereignBrain(session_id="OFFLINE_TEST", memory=tmp_memory)
    b._client = None  # simulate missing SDK

    import enki_ai.core.sovereign_brain as _sb
    original = _sb._GENAI_AVAILABLE
    try:
        _sb._GENAI_AVAILABLE = False
        result = b.query("Will this break?")
        assert "OFFLINE" in result or "not installed" in result.lower() or "google-genai" in result
    finally:
        _sb._GENAI_AVAILABLE = original


# ---------------------------------------------------------------------------
# Live Gemini tests — skipped unless SDK + key are available
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (_GENAI_AVAILABLE and _LIVE_KEY),
    reason="google-genai not installed or GEMINI_API_KEY not set",
)
def test_live_query_returns_nonempty_string(tmp_memory):
    from enki_ai.core.sovereign_brain import SovereignBrain

    b = SovereignBrain(session_id="LIVE_TEST", memory=tmp_memory)
    result = b.query("What is Node 29? Answer in one sentence.")
    assert isinstance(result, str)
    assert len(result.strip()) > 10
