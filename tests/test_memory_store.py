"""
Tests for enki_ai.core.memory_store.
"""

import os
import tempfile
from pathlib import Path

import pytest

from enki_ai.core.memory_store import MemoryStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store(tmp_path):
    """Return a MemoryStore backed by a temp SQLite DB."""
    db = tmp_path / "test_memory.db"
    return MemoryStore(db_path=db, max_turns=10)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def test_db_created(tmp_path):
    db = tmp_path / "sub" / "mem.db"
    MemoryStore(db_path=db)
    assert db.exists()


# ---------------------------------------------------------------------------
# add_turn / get_context
# ---------------------------------------------------------------------------


def test_add_and_retrieve_turn(store):
    store.add_turn("s1", role="user", content="Hello Enki")
    ctx = store.get_context("s1")
    assert len(ctx) == 1
    assert ctx[0]["content"] == "Hello Enki"
    assert ctx[0]["role"] == "user"


def test_multiple_turns_ordered_asc(store):
    for i in range(5):
        store.add_turn("s1", role="user", content=f"msg {i}")
    ctx = store.get_context("s1")
    contents = [t["content"] for t in ctx]
    assert contents == [f"msg {i}" for i in range(5)]


def test_last_n_respected(store):
    for i in range(8):
        store.add_turn("s1", role="enki", content=f"reply {i}")
    ctx = store.get_context("s1", last_n=3)
    assert len(ctx) == 3
    # Should be the 3 most recent (oldest of those 3 first)
    assert ctx[-1]["content"] == "reply 7"


def test_different_sessions_isolated(store):
    store.add_turn("alpha", role="user", content="Alpha turn")
    store.add_turn("beta", role="user", content="Beta turn")
    assert len(store.get_context("alpha")) == 1
    assert len(store.get_context("beta")) == 1
    assert store.get_context("alpha")[0]["content"] == "Alpha turn"


def test_pillar_tags_stored(store):
    store.add_turn("s1", role="user", content="justice query", pillar_tags="Justice,Integrity")
    ctx = store.get_context("s1")
    assert ctx[0]["pillar_tags"] == "Justice,Integrity"


# ---------------------------------------------------------------------------
# Max-turns trimming
# ---------------------------------------------------------------------------


def test_max_turns_trimmed(store):
    # store.max_turns == 10
    for i in range(15):
        store.add_turn("s1", role="user", content=f"t{i}")
    assert store.turn_count("s1") == 10


def test_oldest_turns_removed_first(store):
    for i in range(12):
        store.add_turn("s1", role="user", content=f"t{i}")
    ctx = store.get_context("s1", last_n=10)
    # First surviving turn should be t2 (t0 and t1 trimmed)
    assert ctx[0]["content"] == "t2"


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_finds_match(store):
    store.add_turn("s1", role="user", content="Node 29 is sovereign")
    store.add_turn("s1", role="enki", content="The frequency is locked")
    results = store.search("sovereign")
    assert len(results) == 1
    assert "sovereign" in results[0]["content"]


def test_search_case_insensitive(store):
    store.add_turn("s1", role="user", content="OUSH — the architect speaks")
    results = store.search("oush")
    assert len(results) == 1


def test_search_no_match(store):
    store.add_turn("s1", role="user", content="nothing here")
    assert store.search("xyz_no_match") == []


def test_search_restricted_to_session(store):
    store.add_turn("s1", role="user", content="justice in session one")
    store.add_turn("s2", role="user", content="justice in session two")
    results = store.search("justice", session_id="s1")
    assert len(results) == 1
    assert results[0]["session_id"] == "s1"


# ---------------------------------------------------------------------------
# clear_session
# ---------------------------------------------------------------------------


def test_clear_session(store):
    store.add_turn("s1", role="user", content="will be cleared")
    store.clear_session("s1")
    assert store.get_context("s1") == []


def test_clear_session_does_not_affect_others(store):
    store.add_turn("s1", role="user", content="keep")
    store.add_turn("s2", role="user", content="clear me")
    store.clear_session("s2")
    assert len(store.get_context("s1")) == 1


# ---------------------------------------------------------------------------
# start_session / list_sessions
# ---------------------------------------------------------------------------


def test_start_session_creates_record(store):
    store.start_session("pilot_001", pilot_handle="CassAI")
    sessions = store.list_sessions()
    ids = [s["session_id"] for s in sessions]
    assert "pilot_001" in ids


def test_list_sessions_returns_most_recent_first(store):
    import time
    store.start_session("old_session")
    time.sleep(0.05)
    store.add_turn("new_session", role="user", content="hi")
    sessions = store.list_sessions()
    # new_session was touched more recently
    assert sessions[0]["session_id"] == "new_session"


# ---------------------------------------------------------------------------
# turn_count
# ---------------------------------------------------------------------------


def test_turn_count(store):
    assert store.turn_count("empty") == 0
    store.add_turn("s1", role="user", content="a")
    store.add_turn("s1", role="enki", content="b")
    assert store.turn_count("s1") == 2


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------


def test_module_singleton_is_memory_store():
    from enki_ai.core.memory_store import memory
    assert isinstance(memory, MemoryStore)
