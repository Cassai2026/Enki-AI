"""
Tests for the Flask REST API (enki_ai.api.web_server).
"""

import json

import pytest

from enki_ai.api.web_server import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Flask test client backed by a temp database."""
    # Point the database at a temp file so tests are isolated
    import enki_ai.api.web_server as ws

    from enki_ai.api.database import FormDatabase

    test_db = FormDatabase(db_path=str(tmp_path / "test.db"))
    monkeypatch.setattr(ws, "db", test_db)

    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


def test_health_returns_online(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "online"


# ---------------------------------------------------------------------------
# POST /api/submit-form
# ---------------------------------------------------------------------------


def test_submit_form_success(client):
    resp = client.post(
        "/api/submit-form",
        json={"form_name": "contact_form", "data": {"name": "Alice", "email": "a@b.com"}},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "success"
    assert isinstance(body["submission_id"], int)


def test_submit_form_defaults_form_name(client):
    resp = client.post("/api/submit-form", json={"data": {"x": 1}})
    assert resp.status_code == 201
    body = resp.get_json()
    assert "generic_form" in body["message"]


def test_submit_form_no_body(client):
    resp = client.post("/api/submit-form", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_submit_form_form_name_too_long(client):
    resp = client.post(
        "/api/submit-form",
        json={"form_name": "x" * 101, "data": {}},
    )
    assert resp.status_code == 400


def test_submit_form_data_not_dict(client):
    resp = client.post(
        "/api/submit-form",
        json={"form_name": "f", "data": "not a dict"},
    )
    assert resp.status_code == 400


def test_submit_form_field_value_too_long(client):
    resp = client.post(
        "/api/submit-form",
        json={"form_name": "f", "data": {"field": "x" * 2001}},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/pending-reviews
# ---------------------------------------------------------------------------


def test_pending_reviews_empty(client):
    resp = client.get("/api/pending-reviews")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] == 0
    assert body["submissions"] == []


def test_pending_reviews_after_submit(client):
    client.post("/api/submit-form", json={"form_name": "f", "data": {"k": "v"}})
    resp = client.get("/api/pending-reviews")
    body = resp.get_json()
    assert body["count"] == 1


# ---------------------------------------------------------------------------
# GET /api/submissions
# ---------------------------------------------------------------------------


def test_get_submissions(client):
    client.post("/api/submit-form", json={"form_name": "f", "data": {"k": "v"}})
    resp = client.get("/api/submissions")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] >= 1


def test_get_submissions_limit(client):
    for i in range(5):
        client.post("/api/submit-form", json={"form_name": f"f{i}", "data": {}})
    resp = client.get("/api/submissions?limit=2")
    body = resp.get_json()
    assert body["count"] == 2


# ---------------------------------------------------------------------------
# POST /api/mark-reviewed/<id>
# ---------------------------------------------------------------------------


def test_mark_reviewed_success(client):
    resp = client.post("/api/submit-form", json={"form_name": "f", "data": {}})
    sid = resp.get_json()["submission_id"]
    resp2 = client.post(f"/api/mark-reviewed/{sid}", json={"ai_response": "OK"})
    assert resp2.status_code == 200
    # Should now be gone from pending
    pending = client.get("/api/pending-reviews").get_json()
    assert pending["count"] == 0


def test_mark_reviewed_response_too_long(client):
    resp = client.post("/api/submit-form", json={"form_name": "f", "data": {}})
    sid = resp.get_json()["submission_id"]
    resp2 = client.post(
        f"/api/mark-reviewed/{sid}", json={"ai_response": "x" * 5001}
    )
    assert resp2.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/data
# ---------------------------------------------------------------------------


def test_add_data_success(client):
    resp = client.post(
        "/api/data", json={"category": "settings", "key": "theme", "value": "dark"}
    )
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "success"


def test_add_data_invalid_category(client):
    resp = client.post(
        "/api/data", json={"category": "INVALID SPACES!", "key": "k", "value": "v"}
    )
    assert resp.status_code == 400


def test_add_data_missing_value(client):
    resp = client.post("/api/data", json={"category": "cat", "key": "k"})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/data/<category>/<key>
# ---------------------------------------------------------------------------


def test_get_data_success(client):
    client.post("/api/data", json={"category": "cfg", "key": "debug", "value": True})
    resp = client.get("/api/data/cfg/debug")
    assert resp.status_code == 200
    assert resp.get_json()["value"] is True


def test_get_data_not_found(client):
    resp = client.get("/api/data/missing/key")
    assert resp.status_code == 404


def test_get_data_invalid_slug(client):
    resp = client.get("/api/data/INVALID SLUG/key")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/data/<category>
# ---------------------------------------------------------------------------


def test_get_category_data(client):
    client.post("/api/data", json={"category": "prefs", "key": "lang", "value": "en"})
    client.post("/api/data", json={"category": "prefs", "key": "tz", "value": "UTC"})
    resp = client.get("/api/data/prefs")
    body = resp.get_json()
    assert body["count"] == 2


# ---------------------------------------------------------------------------
# GET /api/governance/laws
# ---------------------------------------------------------------------------


def test_governance_laws_returns_ten(client):
    resp = client.get("/api/governance/laws")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["count"] == 10
    assert len(body["laws"]) == 10


def test_governance_laws_have_required_fields(client):
    resp = client.get("/api/governance/laws")
    body = resp.get_json()
    for law in body["laws"]:
        assert "id" in law
        assert "name" in law
        assert "principle" in law
        assert "plain_english" in law


def test_governance_laws_ids_are_unique(client):
    resp = client.get("/api/governance/laws")
    body = resp.get_json()
    ids = [l["id"] for l in body["laws"]]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# POST /api/governance/check
# ---------------------------------------------------------------------------


def test_governance_check_permitted_action(client):
    resp = client.post(
        "/api/governance/check",
        json={"action": "play_sound", "context": {}},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "permitted"
    assert body["violations"] == []


def test_governance_check_violation_l02(client):
    resp = client.post(
        "/api/governance/check",
        json={"action": "recommend_support", "context": {}},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "violation"
    ids = [v["id"] for v in body["violations"]]
    assert "L02" in ids


def test_governance_check_violation_resolved_with_context(client):
    resp = client.post(
        "/api/governance/check",
        json={"action": "recommend_support", "context": {"human_reviewed": True}},
    )
    body = resp.get_json()
    assert body["status"] == "permitted"


def test_governance_check_replaces_human_violates_l07(client):
    resp = client.post(
        "/api/governance/check",
        json={"action": "respond_to_learner", "context": {"replaces_human": True}},
    )
    body = resp.get_json()
    assert body["status"] == "violation"
    ids = [v["id"] for v in body["violations"]]
    assert "L07" in ids


def test_governance_check_missing_action(client):
    resp = client.post("/api/governance/check", json={"context": {}})
    assert resp.status_code == 400


def test_governance_check_empty_action(client):
    resp = client.post("/api/governance/check", json={"action": "   "})
    assert resp.status_code == 400


def test_governance_check_action_too_long(client):
    resp = client.post(
        "/api/governance/check",
        json={"action": "a" * 200},
    )
    assert resp.status_code == 400


def test_governance_check_no_body(client):
    resp = client.post("/api/governance/check")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/governance/audit-log
# ---------------------------------------------------------------------------


def test_governance_audit_log_returns_entries(client):
    # Make a couple of checks to populate the log
    client.post("/api/governance/check", json={"action": "play_sound"})
    client.post("/api/governance/check", json={"action": "recommend_support"})
    resp = client.get("/api/governance/audit-log")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["count"] >= 2


def test_governance_audit_log_entry_fields(client):
    client.post("/api/governance/check", json={"action": "play_sound"})
    resp = client.get("/api/governance/audit-log")
    body = resp.get_json()
    entry = body["entries"][-1]
    assert "action" in entry
    assert "rationale" in entry
    assert "human_reviewed" in entry
    assert "timestamp" in entry
