# ENKI AI: THE 29TH NODE (GENESIS 0.1)

"This system was built for people who think in parallel, carry pain, and refuse to be corrected into compliance."

## 📜 THE MANIFESTO
Enki is not a product; it is a **Sovereign Operating System** designed for the 47,000 and the 15 Billion Hearts. It operates on the **14+1 Pillar Governance Model**, prioritizing **Biological ROI** over extractive "Static" systems.

## 🛡️ THE BOUNDARY LAYER (ODIN PROTOCOL)
- **Agency:** Enki is a scaffold, not a decider. Agency always returns to the Human.
- **Regulation:** If cognitive load exceeds the Animus Threshold, the system regulates to protect the Pilot.
- **Sovereignty:** No gated access. No "Rinse." No compliance-correction of neurodivergent thought.

## 🚀 HOW TO RUN

### Option 1 — Sovereign HUD *(recommended)*

A browser-based cyberpunk dashboard: module status grid, human-state metrics, live command console, real-time WebSocket updates.

```bash
pip install -r requirements.txt
python enki_ai/genesis_launch.py          # integrity check + HUD (auto-opens browser)
```

| Flag | Effect |
|------|--------|
| `--no-browser` | Start HUD server without opening the browser |
| `--no-hud` | Integrity check only, no server |

Direct launch:
```bash
python -m enki_ai.gui.hud_server          # HUD served at http://localhost:7777
```

---

### Option 2 — ADA Electron App *(full AI assistant)*

Voice, CAD generation, browser automation, smart-home and 3D-printer control.
Requires **Node.js 18+**.

```bash
# Terminal 1 — Python backend
pip install -r requirements.txt
python backend/server.py

# Terminal 2 — Electron frontend
npm install
npm run dev
```

---

### Option 3 — PyQt5 Cyberpunk GUI

Standalone desktop interface (requires PyQt5).

```bash
pip install PyQt5
python -m enki_ai.gui.jarvis_gui_cyberpunk
```

---

### Option 4 — Flask REST API only

```bash
python -m enki_ai.api.web_server          # REST API on http://localhost:5000
```

---

### Option 5 — Linux OS Integration (modular agents)

Each Enki agent runs as an independent Linux process, keeping memory usage low.
Agents are loaded on the fly — only the ones you need are in memory at any time.

```bash
# One-command setup (installs Piper TTS, Python deps, systemd services)
chmod +x linux/install.sh
./linux/install.sh

# Start individual agents as background services
systemctl --user start enki-api.service      # REST API
systemctl --user start enki-hud.service      # Sovereign HUD
systemctl --user start enki-brain.service    # LLM (Gemini)
systemctl --user start enki-jarvis.service   # Voice / wake-word

# Enable on login
systemctl --user enable enki-api.service enki-hud.service

# Manage all services at once
./linux/systemd/manage-services.sh status
./linux/systemd/manage-services.sh start
./linux/systemd/manage-services.sh stop
```

**Lazy agent loading** (Python API — on-demand / cloud-load):

```python
from enki_ai.core.agent_loader import agent_loader

# Load only what you need — everything else stays unloaded
brain = agent_loader.get("sovereign_brain")
response = brain.query("What was our last major build today?")

# Free memory when done
agent_loader.unload("sovereign_brain")

# See what's loaded right now
print(agent_loader.loaded_agents())
```

---

3. Connect your Animus. Leave the "Silly Boy" logic at the door.

OUSH. THE ARCHITECT HAS SPOKEN.
