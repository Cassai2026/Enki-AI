"""
Tests for the form database layer (enki_ai.api.database).
"""

import json
import os
import tempfile

import pytest

from enki_ai.api.database import FormDatabase


@pytest.fixture
def db(tmp_path):
    """Provide a fresh FormDatabase backed by a temp SQLite file."""
    db_file = str(tmp_path / "test.db")
    return FormDatabase(db_path=db_file)


# ---------------------------------------------------------------------------
# submit_form
# ---------------------------------------------------------------------------


def test_submit_form_returns_integer_id(db):
    sid = db.submit_form("test_form", {"name": "Alice"})
    assert isinstance(sid, int)
    assert sid >= 1


def test_submit_form_appears_in_pending(db):
    db.submit_form("contact_form", {"email": "a@b.com"})
    pending = db.get_pending_reviews()
    assert len(pending) == 1
    assert pending[0]["form_name"] == "contact_form"
    assert pending[0]["data"]["email"] == "a@b.com"


def test_submit_multiple_forms(db):
    db.submit_form("form_a", {"x": 1})
    db.submit_form("form_b", {"y": 2})
    pending = db.get_pending_reviews()
    assert len(pending) == 2


# ---------------------------------------------------------------------------
# mark_reviewed
# ---------------------------------------------------------------------------


def test_mark_reviewed_removes_from_pending(db):
    sid = db.submit_form("feedback_form", {"msg": "great"})
    db.mark_reviewed(sid, "Acknowledged.")
    pending = db.get_pending_reviews()
    assert len(pending) == 0


def test_mark_reviewed_without_response(db):
    sid = db.submit_form("generic", {"k": "v"})
    result = db.mark_reviewed(sid)
    assert result is True


def test_mark_reviewed_sets_reviewed_flag(db):
    sid = db.submit_form("flag_form", {"field": "value"})
    db.mark_reviewed(sid)
    submissions = db.get_all_submissions()
    assert submissions[0]["reviewed"] == 1


# ---------------------------------------------------------------------------
# get_all_submissions
# ---------------------------------------------------------------------------


def test_get_all_submissions_respects_limit(db):
    for i in range(5):
        db.submit_form(f"form_{i}", {"index": i})
    result = db.get_all_submissions(limit=3)
    assert len(result) == 3


def test_get_all_submissions_limit_clamped_low(db):
    db.submit_form("form", {"k": "v"})
    # limit=0 should be treated as 1
    result = db.get_all_submissions(limit=0)
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# add_data / get_latest_data / get_data_by_category
# ---------------------------------------------------------------------------


def test_add_and_get_data(db):
    db.add_data("settings", "theme", "dark")
    val = db.get_latest_data("settings", "theme")
    assert val == "dark"


def test_get_latest_data_missing_key(db):
    val = db.get_latest_data("nonexistent", "key")
    assert val is None


def test_add_data_json_round_trip(db):
    payload = {"nested": True, "count": 42}
    db.add_data("config", "payload", payload)
    val = db.get_latest_data("config", "payload")
    assert val == payload


def test_get_data_by_category_returns_all(db):
    db.add_data("prefs", "lang", "en")
    db.add_data("prefs", "theme", "light")
    entries = db.get_data_by_category("prefs")
    keys = {e["key"] for e in entries}
    assert {"lang", "theme"} == keys


def test_get_data_by_category_empty(db):
    entries = db.get_data_by_category("nonexistent")
    assert entries == []


def test_latest_data_returns_most_recent(db):
    db.add_data("settings", "vol", 50)
    db.add_data("settings", "vol", 80)
    val = db.get_latest_data("settings", "vol")
    assert val == 80
