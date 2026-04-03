# Enki AI — Universal Assistant

> *Named after the Sumerian god of wisdom, knowledge, and crafts.*

Enki is a fully-featured, extensible AI assistant written in Python. It ships with a rich interactive CLI, a FastAPI REST + WebSocket server, a plugin architecture for tool-calling, sliding-window conversation memory, and adapters for both OpenAI and Anthropic.

---

## ✨ Features

| Capability | Details |
|---|---|
| **Multi-provider** | OpenAI (`gpt-4o`) and Anthropic (`claude-3-5-sonnet`) — switchable via env var |
| **Tool calling** | Native function-calling loop; plugins auto-expose OpenAI-compatible JSON schemas |
| **Conversation memory** | Sliding-window deque keeps context lean; fully customisable |
| **Streaming** | `async` token-by-token streaming over CLI and WebSocket |
| **REST API** | FastAPI — `POST /chat`, `GET /health`, `GET /plugins`, `POST /reset` |
| **WebSocket** | `/ws/chat` — real-time streaming chat for web clients |
| **Built-in plugins** | Calculator · Web search (DuckDuckGo) · File read/write/list |
| **Extensible** | Drop in any `Plugin` subclass; register it with one line |

---

## 🏗 Architecture

```
enki/
├── core/
│   ├── config.py        # Pydantic-settings — env / .env / defaults
│   ├── memory.py        # ConversationMemory with sliding window
│   └── assistant.py     # Orchestrator — wires provider + memory + plugins
├── providers/
│   ├── base.py          # BaseProvider ABC
│   ├── openai_provider.py
│   └── anthropic_provider.py
├── plugins/
│   ├── base.py          # Plugin ABC + PluginResult
│   ├── calculator.py    # Safe arithmetic evaluator
│   ├── web_search.py    # DuckDuckGo Instant Answer
│   └── file_ops.py      # File read / write / list (sandboxed to cwd)
├── api/
│   ├── app.py           # FastAPI application factory
│   └── routes.py        # REST endpoints + WebSocket
└── cli/
    └── interface.py     # Rich interactive REPL (Typer)
```

---

## 🚀 Quick-start

### 1. Install

```bash
pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### 3. Chat (CLI)

```bash
enki                  # interactive REPL (default: OpenAI)
enki --stream         # stream tokens in real-time
enki --provider anthropic --model claude-3-5-sonnet-20241022
```

CLI commands available inside the REPL:

| Command | Action |
|---|---|
| `/help` | Show command reference |
| `/reset` | Clear conversation history |
| `/plugins` | List active plugins |
| `/stream` | Toggle streaming on/off |
| `/exit` | Quit |

### 4. API server

```bash
enki serve                    # starts on http://0.0.0.0:8000
enki serve --port 9000 --reload
```

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Liveness probe |
| `/chat` | POST | Single-turn chat |
| `/reset` | POST | Clear conversation |
| `/plugins` | GET | List registered tools |
| `/ws/chat` | WS | Streaming chat |

**Example**

```bash
curl -X POST http://localhost:8000/chat \
     -H 'Content-Type: application/json' \
     -d '{"message": "What is the square root of 144?"}'
```

---

## 🔌 Writing a custom plugin

```python
from enki.plugins.base import Plugin, PluginResult

class JokePlugin(Plugin):
    @property
    def name(self) -> str:
        return "tell_joke"

    @property
    def description(self) -> str:
        return "Tell a random programming joke."

    def parameters(self) -> dict:
        return {}

    async def run(self, **_) -> PluginResult:
        return PluginResult(success=True, output={"joke": "Why do programmers prefer dark mode? Because light attracts bugs."})

# Register it:
from enki.core.assistant import Assistant
assistant = Assistant(plugins=[JokePlugin()])
```

---

## 🧪 Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## ⚙️ Configuration reference

All settings can be set via environment variables or `.env`:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `ENKI_PROVIDER` | `openai` | Active provider |
| `ENKI_OPENAI_MODEL` | `gpt-4o` | OpenAI model name |
| `ENKI_ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Anthropic model name |
| `ENKI_MAX_TOKENS` | `4096` | Max completion tokens |
| `ENKI_MEMORY_WINDOW` | `20` | Sliding window size (0 = unlimited) |
| `ENKI_API_HOST` | `0.0.0.0` | API server host |
| `ENKI_API_PORT` | `8000` | API server port |

---

## 📄 License

MIT
