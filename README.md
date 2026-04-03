# Enki-AI — JARVIS

**JARVIS** is a voice-controlled personal assistant for Windows (graceful fallback on Linux/macOS) with:

- 🎙️ Wake-word voice recognition via Google Speech API
- 🔊 Text-to-speech via [Piper TTS](https://github.com/rhasspy/piper)
- 🖥️ Cyberpunk PyQt5 GUI
- 🗄️ SQLite form-submission database with REST API
- 🌐 Web scraper for cassai.co.uk (ODIN module)

---

## Project structure

```
enki_ai/
├── core/
│   ├── config.py           # All paths & constants (override via env vars)
│   ├── jarvis_core.py      # Canonical voice assistant engine
│   └── jarvis_piper_tts.py # Standalone Piper TTS + WAV utilities
├── api/
│   ├── database.py         # SQLite form/data store
│   ├── web_server.py       # Flask REST API
│   └── jarvis_database.py  # JARVIS ↔ database voice helpers
├── gui/
│   └── jarvis_gui_cyberpunk.py  # Neon cyberpunk PyQt5 GUI
└── scrapers/
    └── odin_scraper.py     # cassai.co.uk scraper + conversation parser

archive/          # Old versioned scripts (kept for reference)
tests/            # pytest suite
data/             # SQLite database files (git-ignored)
```

---

## Quick start

### 1. Prerequisites

- Python 3.10+
- [Piper TTS](https://github.com/rhasspy/piper/releases) (Windows AMD64 build recommended)
- A working microphone

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Windows-only extras** (`pycaw`, `comtypes`) are needed for volume control.
> Install separately if you need them:
> ```bash
> pip install pycaw comtypes
> ```

### 3. Configure paths (optional)

All paths have sensible defaults but can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `PIPER_DIR` | `~/Downloads/piper_windows_amd64/piper` | Piper installation directory |
| `PIPER_VOICE` | `en_GB-vctk-medium` | Voice model name (without `.onnx`) |
| `WAKE_WORD` | `jarvis` | Wake word to activate the assistant |
| `DB_PATH` | `data/form_submissions.db` | SQLite database path |
| `API_HOST` | `127.0.0.1` | Flask API host |
| `API_PORT` | `5000` | Flask API port |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |

### 4. Run

**Voice assistant (CLI):**
```bash
python -m enki_ai.core.jarvis_core
```

**Cyberpunk GUI:**
```bash
python -m enki_ai.gui.jarvis_gui_cyberpunk
```

**REST API server:**
```bash
python -m enki_ai.api.web_server
# API available at http://127.0.0.1:5000
```

---

## Voice commands

| Say | Action |
|---|---|
| `Jarvis open chrome` | Open Chrome |
| `Jarvis volume 50` | Set volume to 50% |
| `Jarvis volume up` / `louder` | Increase volume by 10 |
| `Jarvis volume down 20` | Decrease volume by 20 |
| `Jarvis mute` / `unmute` | Mute / unmute |
| `Jarvis help` | List commands |
| `Jarvis shutdown` | Exit |

---

## REST API

Base URL: `http://127.0.0.1:5000`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/submit-form` | Submit a form `{form_name, data}` |
| `GET` | `/api/pending-reviews` | Submissions awaiting review |
| `GET` | `/api/submissions?limit=N` | Recent submissions |
| `POST` | `/api/mark-reviewed/<id>` | Mark submission reviewed `{ai_response?}` |
| `POST` | `/api/data` | Add key-value entry `{category, key, value}` |
| `GET` | `/api/data/<category>/<key>` | Latest value |
| `GET` | `/api/data/<category>` | All entries in category |
| `GET` | `/health` | Health check |

**Example — submit a form:**
```bash
curl -X POST http://127.0.0.1:5000/api/submit-form \
  -H "Content-Type: application/json" \
  -d '{"form_name": "contact_form", "data": {"name": "Alice", "email": "a@b.com"}}'
```

---

## Running tests

```bash
pytest tests/ -v
```

Tests cover the database layer, REST API validation, and command routing — no audio hardware required.

---

## Development

### Project conventions

- **All paths** come from `enki_ai/core/config.py` — never hardcode a path in source files.
- **Logging** uses Python's `logging` module throughout; no bare `print()` in library code.
- **Audio** dependencies (`winsound`, `pycaw`) are imported lazily and fail gracefully on non-Windows.
- **Tests** live in `tests/` and must pass with `pytest tests/` before any PR merge.

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).
See also [Proprietary Use License.docx](Proprietary%20Use%20License.docx) for commercial terms.
