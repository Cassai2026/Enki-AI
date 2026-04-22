"""
enki_ai.core.memory_store
=========================
Persistent conversation-memory for Enki AI.

Every exchange between the Pilot and Enki is stored in a local SQLite database
so that Enki can recall prior context across sessions.  The store intentionally
stays dependency-free (stdlib only) so it works in every environment.

Usage::

    from enki_ai.core.memory_store import memory

    # Record a turn
    session_id = "pilot_session_001"
    memory.add_turn(session_id, role="user",    content="What is Node 29?")
    memory.add_turn(session_id, role="enki",    content="Node 29 is the founding Sovereign node.")

    # Retrieve recent context
    history = memory.get_context(session_id, last_n=10)
    for turn in history:
        print(turn["role"], turn["content"])

    # Search across all sessions
    results = memory.search("Node 29")

Configuration
-------------
Set ``MEMORY_DB_PATH`` in your ``.env`` (or environment) to override the
default database location (``data/enki_memory.db`` relative to the project
root).  Set ``MEMORY_MAX_TURNS`` to cap how many turns are retained per
session (default: 200).
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — read from environment / sensible defaults
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_DEFAULT_DB = _PROJECT_ROOT / "data" / "enki_memory.db"
MEMORY_DB_PATH: Path = Path(os.environ.get("MEMORY_DB_PATH", str(_DEFAULT_DB)))
MEMORY_MAX_TURNS: int = int(os.environ.get("MEMORY_MAX_TURNS", "200"))

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS conversation_turns (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT     NOT NULL,
    role        TEXT     NOT NULL CHECK(role IN ('user','enki','system')),
    content     TEXT     NOT NULL,
    pillar_tags TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_turns_session
    ON conversation_turns (session_id, id);

CREATE TABLE IF NOT EXISTS sessions (
    session_id   TEXT     PRIMARY KEY,
    pilot_handle TEXT,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------


class MemoryStore:
    """
    Persistent SQLite-backed conversation memory.

    Thread-safety: each call opens and closes its own connection so this is
    safe to use from multiple threads (SQLite WAL mode is enabled).
    """

    def __init__(
        self,
        db_path: Path = MEMORY_DB_PATH,
        max_turns: int = MEMORY_MAX_TURNS,
    ) -> None:
        self.db_path = Path(db_path)
        self.max_turns = max_turns
        self._init_db()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        try:
            conn = self._connect()
            conn.executescript(_SCHEMA)
            conn.commit()
            conn.close()
            log.debug("[Memory] DB initialised at %s", self.db_path)
        except Exception as exc:
            log.warning("[Memory] Could not initialise memory DB: %s", exc)

    def _trim(self, conn: sqlite3.Connection, session_id: str) -> None:
        """Remove oldest turns if the session exceeds max_turns."""
        count = conn.execute(
            "SELECT COUNT(*) FROM conversation_turns WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
        excess = count - self.max_turns
        if excess > 0:
            conn.execute(
                """
                DELETE FROM conversation_turns
                WHERE id IN (
                    SELECT id FROM conversation_turns
                    WHERE session_id = ?
                    ORDER BY id ASC
                    LIMIT ?
                )
                """,
                (session_id, excess),
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_session(
        self,
        session_id: str,
        pilot_handle: Optional[str] = None,
    ) -> None:
        """Register (or update) a session record."""
        try:
            conn = self._connect()
            conn.execute(
                """
                INSERT INTO sessions (session_id, pilot_handle, last_active)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_active = excluded.last_active
                """,
                (session_id, pilot_handle, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            log.warning("[Memory] start_session error: %s", exc)

    def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        pillar_tags: Optional[str] = None,
    ) -> None:
        """
        Append one conversation turn to memory.

        Parameters
        ----------
        session_id:
            Unique identifier for this conversation session.
        role:
            ``"user"``, ``"enki"``, or ``"system"``.
        content:
            The spoken/typed message text.
        pillar_tags:
            Comma-separated Pillar names triggered by this turn (optional).
        """
        try:
            conn = self._connect()
            conn.execute(
                """
                INSERT INTO conversation_turns
                    (session_id, role, content, pillar_tags, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content,
                    pillar_tags,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            # Keep session last_active current
            conn.execute(
                """
                INSERT INTO sessions (session_id, last_active)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_active = excluded.last_active
                """,
                (session_id, datetime.now(timezone.utc).isoformat()),
            )
            self._trim(conn, session_id)
            conn.commit()
            conn.close()
            log.debug("[Memory] Turn stored — session=%s role=%s", session_id, role)
        except Exception as exc:
            log.warning("[Memory] add_turn error: %s", exc)

    def get_context(
        self,
        session_id: str,
        last_n: int = 20,
    ) -> list[dict]:
        """
        Return the *last_n* turns for *session_id*, oldest first.

        Each item is a dict with keys: ``id``, ``role``, ``content``,
        ``pillar_tags``, ``created_at``.
        """
        try:
            conn = self._connect()
            rows = conn.execute(
                """
                SELECT id, role, content, pillar_tags, created_at
                FROM (
                    SELECT id, role, content, pillar_tags, created_at
                    FROM conversation_turns
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                ) sub
                ORDER BY id ASC
                """,
                (session_id, last_n),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as exc:
            log.warning("[Memory] get_context error: %s", exc)
            return []

    def search(
        self,
        keyword: str,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Full-text search across stored conversation turns.

        Parameters
        ----------
        keyword:
            Case-insensitive substring to search in ``content``.
        session_id:
            If provided, restrict search to this session only.
        limit:
            Maximum number of results to return.
        """
        try:
            conn = self._connect()
            like = f"%{keyword}%"
            if session_id:
                rows = conn.execute(
                    """
                    SELECT session_id, role, content, pillar_tags, created_at
                    FROM conversation_turns
                    WHERE session_id = ? AND LOWER(content) LIKE LOWER(?)
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (session_id, like, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT session_id, role, content, pillar_tags, created_at
                    FROM conversation_turns
                    WHERE LOWER(content) LIKE LOWER(?)
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (like, limit),
                ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as exc:
            log.warning("[Memory] search error: %s", exc)
            return []

    def clear_session(self, session_id: str) -> None:
        """Delete all turns for *session_id* (irreversible)."""
        try:
            conn = self._connect()
            conn.execute(
                "DELETE FROM conversation_turns WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()
            conn.close()
            log.info("[Memory] Session cleared: %s", session_id)
        except Exception as exc:
            log.warning("[Memory] clear_session error: %s", exc)

    def list_sessions(self) -> list[dict]:
        """Return all known sessions ordered by most recently active."""
        try:
            conn = self._connect()
            rows = conn.execute(
                """
                SELECT session_id, pilot_handle, created_at, last_active
                FROM sessions
                ORDER BY last_active DESC
                """
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as exc:
            log.warning("[Memory] list_sessions error: %s", exc)
            return []

    def turn_count(self, session_id: str) -> int:
        """Return the number of stored turns for *session_id*."""
        try:
            conn = self._connect()
            count = conn.execute(
                "SELECT COUNT(*) FROM conversation_turns WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]
            conn.close()
            return count
        except Exception as exc:
            log.warning("[Memory] turn_count error: %s", exc)
            return 0


# ---------------------------------------------------------------------------
# Module-level singleton — import and use directly
# ---------------------------------------------------------------------------

memory: MemoryStore = MemoryStore()
