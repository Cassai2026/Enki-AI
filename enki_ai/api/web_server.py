"""
Flask REST API for JARVIS form submissions.

Run:
    python -m enki_ai.api.web_server
    # or via batch script / start_assistant.bat
"""

import logging
import os
import re
from typing import Any

from flask import Flask, jsonify, request  # type: ignore[import]

from enki_ai.api.database import db
from enki_ai.core import config

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("jarvis.api")

try:
    from flask_cors import CORS  # type: ignore[import]

    CORS(app)
    log.info("CORS enabled.")
except ImportError:
    log.warning("flask-cors not installed – cross-origin requests may be blocked.")

# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile(r"^[a-z0-9_\-]{1,64}$")

_MAX_FORM_NAME_LEN = 100
_MAX_FORM_DATA_KEYS = 50
_MAX_FIELD_VALUE_LEN = 2000
_MAX_AI_RESPONSE_LEN = 5000


def _validate_slug(value: Any, field: str) -> tuple[bool, str]:
    """Require *value* to be a safe lowercase slug (letters, digits, _, -)."""
    if not isinstance(value, str):
        return False, f"'{field}' must be a string."
    if not _SLUG_RE.match(value):
        return False, (
            f"'{field}' must be 1–64 characters: lowercase letters, digits, "
            "underscores, or hyphens."
        )
    return True, ""


def _validate_form_data(form_data: Any) -> tuple[bool, str]:
    if not isinstance(form_data, dict):
        return False, "'data' must be a JSON object."
    if len(form_data) > _MAX_FORM_DATA_KEYS:
        return False, f"'data' may not contain more than {_MAX_FORM_DATA_KEYS} keys."
    for k, v in form_data.items():
        if not isinstance(k, str) or len(k) > 200:
            return False, "Each key in 'data' must be a string ≤ 200 characters."
        if isinstance(v, str) and len(v) > _MAX_FIELD_VALUE_LEN:
            return (
                False,
                f"Field value for '{k}' exceeds {_MAX_FIELD_VALUE_LEN} characters.",
            )
    return True, ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/api/submit-form", methods=["POST"])
def submit_form():
    """Submit form data to the database."""
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"status": "error", "message": "Request body must be JSON."}), 400

    form_name = body.get("form_name", "generic_form")
    if not isinstance(form_name, str) or len(form_name) > _MAX_FORM_NAME_LEN:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"'form_name' must be a string ≤ {_MAX_FORM_NAME_LEN} characters.",
                }
            ),
            400,
        )

    form_data = body.get("data", {})
    ok, msg = _validate_form_data(form_data)
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400

    try:
        submission_id = db.submit_form(form_name, form_data)
    except Exception as exc:
        log.error("submit_form db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return (
        jsonify(
            {
                "status": "success",
                "submission_id": submission_id,
                "message": f'Form "{form_name}" submitted successfully.',
            }
        ),
        201,
    )


@app.route("/api/pending-reviews", methods=["GET"])
def get_pending_reviews():
    """Return all submissions awaiting AI review."""
    try:
        pending = db.get_pending_reviews()
    except Exception as exc:
        log.error("get_pending_reviews db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return jsonify({"status": "success", "count": len(pending), "submissions": pending})


@app.route("/api/submissions", methods=["GET"])
def get_submissions():
    """Return recent form submissions (``?limit=N``, max 1000)."""
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 1000))
    try:
        submissions = db.get_all_submissions(limit=limit)
    except Exception as exc:
        log.error("get_submissions db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return jsonify(
        {"status": "success", "count": len(submissions), "submissions": submissions}
    )


@app.route("/api/mark-reviewed/<int:submission_id>", methods=["POST"])
def mark_reviewed(submission_id: int):
    """Mark a submission as reviewed, optionally with an AI response."""
    body = request.get_json(silent=True) or {}
    ai_response = body.get("ai_response")

    if ai_response is not None:
        if not isinstance(ai_response, str):
            return (
                jsonify({"status": "error", "message": "'ai_response' must be a string."}),
                400,
            )
        if len(ai_response) > _MAX_AI_RESPONSE_LEN:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"'ai_response' exceeds {_MAX_AI_RESPONSE_LEN} characters.",
                    }
                ),
                400,
            )

    try:
        db.mark_reviewed(submission_id, ai_response)
    except Exception as exc:
        log.error("mark_reviewed db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return jsonify(
        {"status": "success", "message": f"Submission {submission_id} marked as reviewed."}
    )


@app.route("/api/data", methods=["POST"])
def add_data():
    """Add a key-value data entry."""
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"status": "error", "message": "Request body must be JSON."}), 400

    category = body.get("category")
    key = body.get("key")
    value = body.get("value")

    ok, msg = _validate_slug(category, "category")
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400

    ok, msg = _validate_slug(key, "key")
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400

    if value is None:
        return jsonify({"status": "error", "message": "'value' is required."}), 400

    if isinstance(value, str) and len(value) > _MAX_FIELD_VALUE_LEN:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"'value' exceeds {_MAX_FIELD_VALUE_LEN} characters.",
                }
            ),
            400,
        )

    try:
        entry_id = db.add_data(category, key, value)
    except Exception as exc:
        log.error("add_data db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return jsonify({"status": "success", "entry_id": entry_id, "message": "Data entry added."}), 201


@app.route("/api/data/<category>/<key>", methods=["GET"])
def get_data(category: str, key: str):
    """Get the latest value for ``category/key``."""
    ok, msg = _validate_slug(category, "category")
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400
    ok, msg = _validate_slug(key, "key")
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400

    try:
        value = db.get_latest_data(category, key)
    except Exception as exc:
        log.error("get_data db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    if value is None:
        return (
            jsonify(
                {
                    "status": "not_found",
                    "message": f"No data found for {category}/{key}.",
                }
            ),
            404,
        )

    return jsonify({"status": "success", "category": category, "key": key, "value": value})


@app.route("/api/data/<category>", methods=["GET"])
def get_category_data(category: str):
    """Return all entries in *category*."""
    ok, msg = _validate_slug(category, "category")
    if not ok:
        return jsonify({"status": "error", "message": msg}), 400

    try:
        entries = db.get_data_by_category(category)
    except Exception as exc:
        log.error("get_category_data db error: %s", exc)
        return jsonify({"status": "error", "message": "Database error."}), 500

    return jsonify(
        {"status": "success", "category": category, "count": len(entries), "entries": entries}
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "online",
            "database": "connected" if os.path.exists(db.db_path) else "not found",
        }
    )


@app.route("/", methods=["GET"])
def index():
    """API documentation."""
    return jsonify(
        {
            "name": "JARVIS Form Database API",
            "endpoints": {
                "POST /api/submit-form": "Submit form data",
                "GET  /api/pending-reviews": "Submissions pending AI review",
                "GET  /api/submissions": "Recent submissions (?limit=N)",
                "POST /api/mark-reviewed/<id>": "Mark submission as reviewed",
                "POST /api/data": "Add key-value data entry",
                "GET  /api/data/<category>": "All entries in a category",
                "GET  /api/data/<category>/<key>": "Latest value for a key",
                "GET  /health": "Health check",
            },
        }
    )


if __name__ == "__main__":
    log.info("Starting JARVIS Form Database API on http://%s:%d", config.API_HOST, config.API_PORT)
    app.run(host=config.API_HOST, port=config.API_PORT, debug=False)
