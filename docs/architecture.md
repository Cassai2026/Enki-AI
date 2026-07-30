# Enki AI Architecture

## Purpose

Enki AI combines a Python backend platform with a React + Electron desktop client.

## High-level components

1. **UI layer** (`src/`, `electron/`): desktop shell and frontend interactions.
2. **Agent/runtime layer** (`enki_ai/agents/`): real-time agent orchestration and tool execution.
3. **API layer** (`enki_ai/api/`): HTTP endpoints and persistence entrypoints.
4. **Core services** (`enki_ai/core/`): configuration, governance, memory, shared runtime utilities.
5. **Knowledge-base modules** (`enki_ai/knowledge_base/`): ingestion and governance support scripts.
6. **Tests** (`tests/`): regression and behavior coverage for core components.

## Runtime model

1. Frontend connects to backend services for assistant actions.
2. Agent layer routes tool calls and enforces runtime constraints.
3. Core modules provide shared state and policy checks.
4. API layer exposes integration points and data persistence.

## Scope boundaries

- Production work should target `enki_ai/`, `src/`, `electron/`, and `tests/`.
- `enki_ai/knowledge_base/` is the canonical location for knowledge-base scripts.
- Experimental research work should remain isolated from production paths.
- Historical and narrative artifacts belong in `docs/archive/`.
