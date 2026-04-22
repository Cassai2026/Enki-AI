# Contributing to Enki AI

> "This system was built for people who think in parallel, carry pain, and refuse to be corrected into compliance."

Thanks for wanting to contribute to the 29th Node. This guide gets you from zero to running in the shortest path possible.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Variables](#environment-variables)
4. [Project Structure](#project-structure)
5. [Running the Tests](#running-the-tests)
6. [Run Modes](#run-modes)
7. [Governance Model](#governance-model)
8. [Contribution Guidelines](#contribution-guidelines)
9. [Branch & PR Workflow](#branch--pr-workflow)

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | ≥ 3.11 | `python3 --version` |
| pip | latest | `pip install --upgrade pip` |
| Node.js | ≥ 18 | Only for the Electron frontend |
| npm | ≥ 9 | Bundled with Node.js |
| Docker (optional) | ≥ 24 | For `docker compose up` |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Cassai2026/Enki-AI.git
cd Enki-AI

# 2. Copy and fill environment variables
cp .env.template .env
# Edit .env — see the "Environment Variables" section below

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the Sovereign HUD (recommended entry point)
python enki_ai/genesis_launch.py

# 5. Or run just the REST API
python -m enki_ai.api.web_server
```

### Docker (full stack)

```bash
cp .env.template .env   # fill in your values
docker compose up --build
```

| Service | URL |
|---------|-----|
| REST API | http://localhost:5000 |
| Sovereign HUD | http://localhost:7777 |
| Vite frontend | http://localhost:5173 |

---

## Environment Variables

Copy `.env.template` to `.env`. Every variable has an inline comment explaining its purpose. Key ones:

| Variable | Required | Description |
|----------|----------|-------------|
| `ENKI_API_KEY` | Yes | Google GenAI API key for LLM calls |
| `SOVEREIGN_ID` | No | Node identifier (default `ROOT_29`) |
| `DB_PATH` | No | SQLite form-submissions DB path |
| `MEMORY_DB_PATH` | No | Conversation memory DB path |
| `MEMORY_MAX_TURNS` | No | Max turns retained per session (default 200) |
| `API_HOST` / `API_PORT` | No | Flask REST API bind address |
| `HUD_PORT` | No | Sovereign HUD WebSocket port (default 7777) |
| `LOG_LEVEL` | No | Python log level (`DEBUG`/`INFO`/`WARNING`) |
| `PIPER_DIR` | No | Path to Piper TTS binary (voice output) |
| `WAKE_WORD` | No | Activation word (default `jarvis`) |

---

## Project Structure

```
enki_ai/
├── core/           Core logic — config, governance law, memory store,
│                   health-check, shell, middleware, console
├── api/            Flask REST API (web_server.py, database.py)
├── gui/            HUD server (FastAPI + WebSocket) and PyQt5 GUI
├── game_engine/    Individual engine modules (justice, roi, forensics, etc.)
├── scrapers/       Web scrapers for legal/governance data
├── skills/         Plug-in skills
├── knowledge_base/ Knowledge base helpers
└── mobile/         Expo React Native companion app

tests/              pytest test suite (run with: pytest tests/)
docs/               Mission documents (ingested by ingest_mission_data.py)
.github/workflows/  CI (pytest on every push)
```

**Key entry points:**

| Command | What it starts |
|---------|---------------|
| `python enki_ai/genesis_launch.py` | Integrity check + Sovereign HUD |
| `python -m enki_ai.gui.hud_server` | HUD only (port 7777) |
| `python -m enki_ai.api.web_server` | Flask REST API (port 5000) |
| `python -m enki_ai.core.ingest_mission_data` | Ingest docs → SQLite |

---

## Running the Tests

```bash
# Install test dependencies (if not already in requirements.txt)
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=enki_ai --cov-report=term-missing

# Run a specific file
pytest tests/test_governance.py -v
```

Tests that need optional heavy deps (`cv2`, `mediapipe`, `playwright`,
`google-genai`, `build123d`) are guarded with `pytest.skip` — they will be
skipped automatically if those packages are not installed. CI runs only the
core test suite.

---

## Run Modes

### Option 1 — Sovereign HUD *(recommended)*

```bash
python enki_ai/genesis_launch.py           # opens browser automatically
python enki_ai/genesis_launch.py --no-browser  # headless
python -m enki_ai.gui.hud_server           # direct launch
```

### Option 2 — ADA Electron App

```bash
# Terminal 1
python -m enki_ai.agents.server   # or: python backend/server.py

# Terminal 2
npm install && npm run dev
```

### Option 3 — PyQt5 GUI

```bash
pip install PyQt5
python -m enki_ai.gui.jarvis_gui_cyberpunk
```

### Option 4 — REST API only

```bash
python -m enki_ai.api.web_server   # http://localhost:5000
```

### Option 5 — Mobile (Expo)

```bash
cd mobile
npm install
npm start   # Expo dev server — scan QR with Expo Go app
```

---

## Governance Model

Enki AI is governed by the **Dimensional Human-Centred AI Governance Model
(DHCAIGM)** — 10 laws encoded in `enki_ai/core/governance.py`.

You can inspect and test the laws through the REST API:

```bash
# List all laws
curl http://localhost:5000/api/governance/laws

# Check whether an action is compliant
curl -X POST http://localhost:5000/api/governance/check \
     -H "Content-Type: application/json" \
     -d '{"action": "recommend_support", "context": {"human_reviewed": true}}'

# View the audit log
curl http://localhost:5000/api/governance/audit-log
```

Any new feature that generates AI recommendations **must** call
`engine.assert_permitted(action, context)` before executing, and
`engine.log_decision(action, rationale)` afterwards.

---

## Contribution Guidelines

1. **No Rinse. No Static.** Do not compliance-correct neurodivergent thought
   patterns or writing styles in docs, comments, or commit messages.
2. **Agency first.** Features that reduce human agency are rejected.
3. **Governance-compliant code.** Any AI-driven action must pass through
   `enki_ai.core.governance.engine`.
4. **Test your changes.** Add or update tests in `tests/`. CI will run them.
5. **Pin new dependencies.** If you add a package to `requirements.txt`,
   specify the exact version (`package==X.Y.Z`).
6. **Use `enki_ai/core/config.py`** for all paths and tunables — no
   hardcoded paths in application code.
7. **Memory store.** Conversation turns should be persisted via
   `enki_ai.core.memory_store.memory.add_turn(...)`.

---

## Branch & PR Workflow

```
main  ──────────────────────────────────────────────────►
         │                              │
         └──► feature/your-feature ────┘  (PR → main)
```

1. Branch off `main`: `git checkout -b feature/my-feature`
2. Make your changes, add tests.
3. Run `pytest tests/` — all core tests must pass.
4. Open a PR against `main`.
5. CI runs automatically. Address any failures before requesting review.

---

OUSH. THE ARCHITECT HAS SPOKEN.
