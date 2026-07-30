# Enki AI

Enki AI is a hybrid Python + Electron assistant platform with real-time voice interaction, tool execution, CAD generation, browser automation, and optional smart-home and printing integrations.

## What this repository contains

- **Desktop app**: Electron shell with a React frontend (`electron/`, `src/`)
- **Backend services**: FastAPI/Socket.IO and Flask components (`enki_ai/agents/`, `enki_ai/api/`)
- **Core platform logic**: config, runtime services, and shared modules (`enki_ai/core/`)
- **Research modules**: experimental game/simulation and mobile workstreams (`game_engine/`, `mobile/`)

## Quick start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 2. Install dependencies

```bash
pip install -r requirements.txt
npm install
```

### 3. Configure environment

Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run in development mode

```bash
# Full desktop app (frontend + Electron)
npm run dev
```

```bash
# Backend only (for API/service debugging)
python -m enki_ai.agents.server
```

## Project structure

```text
Enki-AI/
├── enki_ai/            # Python package (agents, API, core, integrations)
├── src/                # React frontend
├── electron/           # Electron main process
├── mobile/             # Experimental mobile client
├── game_engine/        # Experimental simulation modules
├── docs/               # Documentation and archived research materials
├── requirements.txt    # Python dependencies
└── package.json        # Node dependencies
```

## Security and data handling

- Keep `.env` private and never commit secrets.
- Face-auth reference assets and session state should be treated as sensitive local data.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Engineering docs

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Release checklist](docs/release-checklist.md)

## License

- Code: [GPL-3.0](LICENSE)
- Creative assets: [CC BY-NC-SA 4.0](LICENSE-CC)
