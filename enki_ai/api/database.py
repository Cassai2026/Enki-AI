# -*- coding: utf-8 -*-
"""
SQLite-backed form submission and key-value data store for JARVIS.
"""

import json
import logging
import os
import sqlite3
from typing import Any, List, Optional

from enki_ai.core import config

log = logging.getLogger(__name__)


class FormDatabase:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or config.DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_database(self) -> None:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_name TEXT    NOT NULL,
                    data      TEXT    NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed  BOOLEAN  DEFAULT 0,
                    notes     TEXT
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS data_entries (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    category  TEXT    NOT NULL,
                    key       TEXT    NOT NULL,
                    value     TEXT    NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS review_queue (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    status        TEXT    DEFAULT 'pending',
                    ai_response   TEXT,
                    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
                )
                """
            )
            conn.commit()
        log.debug("Database initialised at %s", self.db_path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    @staticmethod
    def _json_encode(value: Any) -> str:
        return json.dumps(value) if not isinstance(value, str) else value

    @staticmethod
    def _json_decode(value: str) -> Any:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    # ------------------------------------------------------------------
    # Form submissions
    # ------------------------------------------------------------------

    def submit_form(self, form_name: str, form_data: dict) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO form_submissions (form_name, data) VALUES (?, ?)",
                (form_name, json.dumps(form_data)),
            )
            sid = c.lastrowid
            c.execute("INSERT INTO review_queue (submission_id) VALUES (?)", (sid,))
            conn.commit()
        log.info("Form submitted: id=%d name=%s", sid, form_name)
        return sid

    def mark_reviewed(
        self, submission_id: int, ai_response: Optional[str] = None
    ) -> bool:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE form_submissions SET reviewed = 1 WHERE id = ?",
                (submission_id,),
            )
            if ai_response:
                c.execute(
                    "UPDATE review_queue SET status='completed', ai_response=? WHERE submission_id=?",
                    (ai_response, submission_id),
                )
            else:
                c.execute(
                    "UPDATE review_queue SET status='completed' WHERE submission_id=?",
                    (submission_id,),
                )
            conn.commit()
        log.info("Submission %d marked reviewed.", submission_id)
        return True

    def get_pending_reviews(self) -> List[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                """
                SELECT fs.id, fs.form_name, fs.data, fs.timestamp,
                       rq.id AS review_id
                FROM   form_submissions fs
                JOIN   review_queue     rq ON fs.id = rq.submission_id
                WHERE  rq.status = 'pending'
                ORDER  BY fs.timestamp DESC
                """
            )
            rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r["data"] = self._json_decode(r["data"])
        return rows

    def get_all_submissions(self, limit: int = 100) -> List[dict]:
        limit = max(1, min(limit, 1000))
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                "SELECT * FROM form_submissions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r["data"] = self._json_decode(r["data"])
        return rows

    # ------------------------------------------------------------------
    # Key-value data store
    # ------------------------------------------------------------------

    def add_data(self, category: str, key: str, value: Any) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO data_entries (category, key, value) VALUES (?, ?, ?)",
                (category, key, self._json_encode(value)),
            )
            eid = c.lastrowid
            conn.commit()
        log.debug("Data entry added: category=%s key=%s", category, key)
        return eid

    def get_latest_data(self, category: str, key: str) -> Any:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                "SELECT value FROM data_entries WHERE category=? AND key=? ORDER BY id DESC LIMIT 1",
                (category, key),
            )
            result = c.fetchone()
        if result:
            return self._json_decode(result["value"])
        return None

    def get_data_by_category(self, category: str) -> List[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                "SELECT * FROM data_entries WHERE category=? ORDER BY timestamp DESC",
                (category,),
            )
            rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r["value"] = self._json_decode(r["value"])
        return rows


# Module-level singleton used by web_server and jarvis_database
db = FormDatabase()
