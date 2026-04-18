# backend/ — Moved to enki_ai/agents/

All Python agent modules that were previously in this directory have been
moved to [`enki_ai/agents/`](../enki_ai/agents/) as part of consolidating
the project into a single `enki_ai` Python package.

## Starting the server

```bash
# From the repo root
python -m enki_ai.agents.server
```

## Old path → New path

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
| `backend/settings.json` | `enki_ai/agents/settings.json` |
| `backend/face_landmarker.task` | `enki_ai/agents/face_landmarker.task` |
