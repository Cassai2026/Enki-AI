#!/usr/bin/env python3
"""
ingest_mission_data.py  (root-level entry point)
=================================================
.. deprecated::
    Run this script via the package instead::

        python -m enki_ai.core.ingest_mission_data [--docs <path>] [--db <path>]

    This root-level script is kept for backwards compatibility only and may be
    removed in a future release.

Reads every file in the /docs folder (DOCX and PDF), extracts plain text,
and stores structured entries in ``enki_knowledge.db`` (SQLite).

Tables
------
Forensic_Evidence   — Field reports, site logs, GPS/location data
System_Logic        — Technical stack docs, execution notes, backend logic
Personal_Mandate    — Founding documents, mission logs, governance charters

Each row is tagged with one or more of the 14 Pillars (comma-separated).

Usage
-----
    python ingest_mission_data.py [--docs <path>] [--db <path>]

Defaults: docs → ./docs,  db → ./enki_knowledge.db
"""

from __future__ import annotations

import warnings
warnings.warn(
    "Running ingest_mission_data.py from the project root is deprecated. "
    "Use 'python -m enki_ai.core.ingest_mission_data' instead. "
    "This root-level entry point will be removed in a future release.",
    DeprecationWarning,
    stacklevel=1,
)

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Optional heavy-dependency imports — warn gracefully if absent
# ---------------------------------------------------------------------------

try:
    from docx import Document as DocxDocument  # type: ignore[import]
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False
    print("[INGEST] python-docx not found. DOCX files will be skipped. "
          "Install with: pip install python-docx")

try:
    import PyPDF2  # type: ignore[import]
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False
    print("[INGEST] PyPDF2 not found. PDF files will be skipped. "
          "Install with: pip install PyPDF2")

# ---------------------------------------------------------------------------
# 14 Pillars
# ---------------------------------------------------------------------------

THE_14_PILLARS: list[str] = [
    "Sloth",
    "Charity",
    "Prudence",
    "Justice",
    "Fortitude",
    "Temperance",
    "Faith",
    "Hope",
    "Humility",
    "Diligence",
    "Kindness",
    "Patience",
    "Gratitude",
    "Integrity",
]

# Keyword hints used to auto-tag entries with relevant Pillars.
# Each pillar maps to a list of case-insensitive substrings.
_PILLAR_KEYWORDS: dict[str, list[str]] = {
    "Sloth":       ["delay", "inactive", "idle", "slow"],
    "Charity":     ["charity", "donation", "giving", "support", "fund"],
    "Prudence":    ["prudent", "careful", "risk", "decision", "audit"],
    "Justice":     ["justice", "evidence", "forensic", "legal", "court"],
    "Fortitude":   ["fortitude", "courage", "resilience", "persist"],
    "Temperance":  ["temperance", "balance", "moderate", "control"],
    "Faith":       ["faith", "trust", "belief", "mission", "vision"],
    "Hope":        ["hope", "future", "goal", "potential"],
    "Humility":    ["humility", "humble", "acknowledge", "learn"],
    "Diligence":   ["diligence", "effort", "work", "task", "execution"],
    "Kindness":    ["kind", "empathy", "compassion", "care"],
    "Patience":    ["patient", "wait", "endure", "long-term"],
    "Gratitude":   ["gratitude", "thank", "appreciate"],
    "Integrity":   ["integrity", "honest", "transparent", "sovereign"],
}


def _auto_tag_pillars(text: str) -> str:
    """Return a comma-separated string of Pillar names matched in *text*."""
    text_lower = text.lower()
    matched = [
        pillar
        for pillar, keywords in _PILLAR_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]
    return ",".join(matched) if matched else "Integrity"  # default to Integrity


# ---------------------------------------------------------------------------
# Categorisation heuristics
# ---------------------------------------------------------------------------

_FORENSIC_HINTS = re.compile(
    r"\b(forensic|evidence|GPS|location|site|stinking|ditch|incident|"
    r"report|witness|case|log|field|scene)\b",
    re.IGNORECASE,
)

_SYSTEM_HINTS = re.compile(
    r"\b(technology|stack|backend|server|kernel|algorithm|execution|"
    r"system|code|API|database|pipeline|agent|LLM|AI|model|gesture|"
    r"hand|spatial|video|audio|WebSocket)\b",
    re.IGNORECASE,
)

_MANDATE_HINTS = re.compile(
    r"\b(mandate|mission|founding|vision|charter|governance|sovereign|"
    r"pillar|cohort|constitution|declaration|proposal|fund)\b",
    re.IGNORECASE,
)


def _classify(filename: str, text: str) -> str:
    """Return the table name best matching the document content."""
    scores = {
        "Forensic_Evidence": len(_FORENSIC_HINTS.findall(text)),
        "System_Logic":      len(_SYSTEM_HINTS.findall(text)),
        "Personal_Mandate":  len(_MANDATE_HINTS.findall(text)),
    }
    return max(scores, key=scores.get)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_docx(path: Path) -> Optional[str]:
    if not _DOCX_AVAILABLE:
        return None
    try:
        doc = DocxDocument(str(path))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except Exception as exc:
        print(f"[INGEST] Could not read DOCX '{path.name}': {exc}")
        return None


def _extract_pdf(path: Path) -> Optional[str]:
    if not _PDF_AVAILABLE:
        return None
    try:
        text_parts: list[str] = []
        with open(path, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:
        print(f"[INGEST] Could not read PDF '{path.name}': {exc}")
        return None


def _extract_html(path: Path) -> Optional[str]:
    """Very lightweight HTML text extraction (strips tags)."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"&[a-z]+;", " ", text)
        return " ".join(text.split())
    except Exception as exc:
        print(f"[INGEST] Could not read HTML '{path.name}': {exc}")
        return None


def extract_text(path: Path) -> Optional[str]:
    """Dispatch to the appropriate extractor based on file extension."""
    ext = path.suffix.lower()
    if ext == ".docx":
        return _extract_docx(path)
    if ext == ".pdf":
        return _extract_pdf(path)
    if ext in {".html", ".htm"}:
        return _extract_html(path)
    # Plain-text fallback for .txt, .md, .bat, etc.
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"[INGEST] Could not read '{path.name}': {exc}")
        return None


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS Forensic_Evidence (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    pillars     TEXT    NOT NULL,
    gps_hint    TEXT,
    keywords    TEXT,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS System_Logic (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    pillars     TEXT    NOT NULL,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Personal_Mandate (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    pillars     TEXT    NOT NULL,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

_GPS_PATTERN = re.compile(
    r"(?:GPS|lat(?:itude)?|lon(?:gitude)?|coord(?:inate)?)[:\s]*"
    r"(-?\d{1,3}\.\d+)[°,\s]+(-?\d{1,3}\.\d+)",
    re.IGNORECASE,
)

_KEYWORD_PATTERN = re.compile(
    r"\b(stinking\s+ditch|forensic|evidence|incident|report|GPS|coordinate|"
    r"location|site\s+log|field\s+note)\b",
    re.IGNORECASE,
)


def _extract_gps_hint(text: str) -> Optional[str]:
    m = _GPS_PATTERN.search(text)
    if m:
        return f"{m.group(1)}, {m.group(2)}"
    return None


def _extract_keywords(text: str) -> str:
    matches = {m.group(0).lower() for m in _KEYWORD_PATTERN.finditer(text)}
    return ",".join(sorted(matches))


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def insert_entry(conn: sqlite3.Connection, table: str, source_file: str,
                 content: str, pillars: str,
                 gps_hint: Optional[str] = None,
                 keywords: Optional[str] = None) -> None:
    if table == "Forensic_Evidence":
        conn.execute(
            "INSERT INTO Forensic_Evidence "
            "(source_file, content, pillars, gps_hint, keywords) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_file, content, pillars, gps_hint, keywords),
        )
    elif table == "System_Logic":
        conn.execute(
            "INSERT INTO System_Logic (source_file, content, pillars) "
            "VALUES (?, ?, ?)",
            (source_file, content, pillars),
        )
    else:
        conn.execute(
            "INSERT INTO Personal_Mandate (source_file, content, pillars) "
            "VALUES (?, ?, ?)",
            (source_file, content, pillars),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Knowledge search helper (used by ada.py for PINCH queries)
# ---------------------------------------------------------------------------

def search_forensic_entry(db_path: str, keyword: str) -> Optional[dict]:
    """
    Return the single most relevant Forensic_Evidence row matching *keyword*.

    Searches source_file, content, and keywords columns (case-insensitive
    LIKE).  Returns a dict with ``source_file``, ``content`` (truncated to
    500 chars), ``pillars``, and ``gps_hint``, or ``None`` if nothing is found.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        like = f"%{keyword}%"
        cur.execute(
            """
            SELECT source_file, content, pillars, gps_hint
            FROM   Forensic_Evidence
            WHERE  LOWER(content)     LIKE LOWER(?)
               OR  LOWER(source_file) LIKE LOWER(?)
               OR  LOWER(keywords)    LIKE LOWER(?)
            LIMIT 1
            """,
            (like, like, like),
        )
        row = cur.fetchone()
        conn.close()
        if row is None:
            return None
        return {
            "source_file": row["source_file"],
            "content":     row["content"][:500],
            "pillars":     row["pillars"],
            "gps_hint":    row["gps_hint"],
        }
    except Exception as exc:
        print(f"[INGEST] search_forensic_entry error: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main ingest routine
# ---------------------------------------------------------------------------

_SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".html", ".htm", ".txt", ".md"}


def ingest(docs_dir: Path, db_path: Path) -> None:
    """Ingest all supported files from *docs_dir* into *db_path*."""
    conn = init_db(db_path)

    files = [
        p for p in docs_dir.iterdir()
        if p.is_file() and p.suffix.lower() in _SUPPORTED_EXTENSIONS
    ]

    if not files:
        print(f"[INGEST] No supported files found in '{docs_dir}'.")
        conn.close()
        return

    inserted = 0
    skipped = 0

    for path in sorted(files):
        print(f"[INGEST] Processing: {path.name}")
        text = extract_text(path)
        if not text or len(text.strip()) < 20:
            print(f"[INGEST]   ↳ Skipped (empty or too short).")
            skipped += 1
            continue

        table   = _classify(path.name, text)
        pillars = _auto_tag_pillars(text)
        gps     = _extract_gps_hint(text)
        kws     = _extract_keywords(text)

        insert_entry(conn, table, path.name, text.strip(),
                     pillars, gps, kws)
        print(f"[INGEST]   ↳ Stored in '{table}' | Pillars: {pillars}")
        inserted += 1

    conn.close()
    print(
        f"\n[INGEST] Done — {inserted} entries stored, {skipped} skipped.\n"
        f"         Database: {db_path.resolve()}"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest /docs mission data into enki_knowledge.db"
    )
    parser.add_argument(
        "--docs",
        default=str(Path(__file__).resolve().parent / "docs"),
        help="Path to the docs folder (default: ./docs)",
    )
    parser.add_argument(
        "--db",
        default=str(Path(__file__).resolve().parent / "enki_knowledge.db"),
        help="Path to the output SQLite database (default: ./enki_knowledge.db)",
    )
    args = parser.parse_args()

    ingest(Path(args.docs), Path(args.db))
