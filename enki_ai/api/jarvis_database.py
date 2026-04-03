"""
JARVIS voice-command integration with the form database.
"""

import logging

from enki_ai.api.database import db

log = logging.getLogger(__name__)


def review_pending_submissions() -> str:
    """Return a human-readable summary of pending form submissions."""
    pending = db.get_pending_reviews()
    if not pending:
        return "No pending submissions to review."

    lines = [f"You have {len(pending)} submission(s) awaiting review."]
    for i, submission in enumerate(pending, 1):
        lines.append(
            f"\nSubmission {i}: {submission['form_name']} — "
            f"submitted {submission['timestamp']}\n"
            f"Data: {submission['data']}"
        )
    return "\n".join(lines)


def process_submissions_voice() -> str:
    """Process all pending submissions and mark them reviewed."""
    pending = db.get_pending_reviews()
    if not pending:
        return "No submissions to process."

    lines = [f"Processing {len(pending)} submission(s)."]
    for submission in pending:
        data = submission["data"]
        form_type = submission["form_name"]

        if form_type == "contact_form":
            response = f"Contact request from {data.get('name', 'Unknown')} received."
        elif form_type == "feedback_form":
            response = f"Feedback received: {data.get('feedback', 'No content')}."
        else:
            response = f"{form_type} submitted."

        db.mark_reviewed(submission["id"], response)
        lines.append(f"✓ {response}")

    return "\n".join(lines)


def get_submission_summary() -> str:
    """Return a brief summary of the most recent submissions."""
    all_submissions = db.get_all_submissions(limit=10)
    if not all_submissions:
        return "No submissions in database."

    lines = [f"Database contains {len(all_submissions)} recent submission(s):"]
    for sub in all_submissions:
        reviewed = "Yes" if sub["reviewed"] else "No"
        lines.append(f"  - {sub['form_name']} on {sub['timestamp']} (Reviewed: {reviewed})")
    return "\n".join(lines)


def add_user_setting(setting_name: str, value) -> str:
    """Persist a user preference to the database."""
    db.add_data("user_settings", setting_name, value)
    return f"Setting '{setting_name}' set to {value}."


def get_user_setting(setting_name: str, default=None):
    """Retrieve a user preference; returns *default* if not set."""
    value = db.get_latest_data("user_settings", setting_name)
    return value if value is not None else default
