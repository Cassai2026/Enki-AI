# backend/ — API Entry Point

`backend/` is the **API entry point layer** for Enki AI.  All core enforcer
logic, kernel ingestion, and agent business logic lives in the
[`enki_ai/`](../enki_ai/) package, organised as follows:

| Sub-package | Purpose |
|---|---|
| `enki_ai/core/` | Core enforcer, governance engine, kernel ingestion, config |
| `enki_ai/agents/` | FastAPI server, ADA agent, tools, device agents |
| `enki_ai/api/` | REST API helpers, database models |
| `enki_ai/gui/` | Desktop GUI |
| `enki_ai/scrapers/` | Data scrapers |

**Do not add business logic here.**  This folder exists only to document the
entry-point convention.  The live server is started with:

```bash
# From the repo root
python -m enki_ai.agents.server
```

## Canonical module locations (old path → new path)

| Old | New |
|-----|-----|
| `backend/server.py` | `enki_ai/agents/server.py` |
| `backend/ada.py` | `enki_ai/agents/ada.py` |
| `backend/tools.py` | `enki_ai/agents/tools.py` |
| `backend/cad_agent.py` | `enki_ai/agents/cad_agent.py` |
| `backend/web_agent.py` | `enki_ai/agents/web_agent.py` |
| `backend/kasa_agent.py` | `enki_ai/agents/kasa_agent.py` |
| `backend/printer_agent.py` | `enki_ai/agents/printer_agent.py` |
| `backend/authenticator.py` | `enki_ai/agents/authenticator.py` |
| `backend/capture_face.py` | `enki_ai/agents/capture_face.py` |
| `backend/hand_movement.py` | `enki_ai/agents/hand_movement.py` |
| `backend/project_manager.py` | `enki_ai/agents/project_manager.py` |
| `sdg_enforcer.py` (root) | `enki_ai/core/sdg_enforcer.py` |
| `ingest_mission_data.py` (root) | `enki_ai/core/ingest_mission_data.py` |
| `sovereign_ingest.py` (root) | `enki_ai/core/sovereign_ingest.py` |
