# Contributing to Enki AI

Thanks for contributing. This guide defines the minimum engineering bar for changes in this repository.

## Development setup

1. Install Python 3.11+ and Node.js 18+.
2. Copy `.env.template` to `.env` and set required keys.
3. Install dependencies:
   - `pip install -r requirements.txt`
   - `npm install`

## Repository boundaries

- **Core product code**: `enki_ai/`, `src/`, `electron/`, `backend/`
- **Tests**: `tests/`
- **Operational docs**: `README.md`, `DATABASE_README.md`, `docs/architecture.md`, `docs/roadmap.md`
- **Non-core/archived materials**: `docs/archive/` and experimental folders such as `mobile/`, `game_engine/`

Do not add generated files or narrative artifacts to the repository root.

## Required checks before merge

1. `pytest tests/ -v`
2. `npm run build`

All pull requests should pass CI before merge.

## Pull request expectations

1. Keep PRs focused and small enough to review quickly.
2. Explain why the change is needed and call out any behavior impact.
3. Add or update tests when behavior changes.
4. Avoid unrelated refactors in the same PR.

## Security and secrets

- Never commit `.env`, keys, or credentials.
- Treat local biometric/reference assets as sensitive data.
- Do not include personal or legal documents in product directories.
