"""
Enki AI — Sovereign HUD Server

A lightweight FastAPI web-based HUD that displays real-time system status,
game-engine module health, human state metrics, and a command console.

Run:
    python -m enki_ai.gui.hud_server
    # Then open: http://localhost:7777

Or import and call ``run()`` to start programmatically (e.g. from genesis_launch.py).
"""

import asyncio
import json
import logging
import math
import os
import random
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
_GAME_ENGINE_DIR = _PACKAGE_ROOT / "game_engine"
_CORE_DIR = _PACKAGE_ROOT / "core"
_API_DIR = _PACKAGE_ROOT / "api"
_GUI_DIR = _PACKAGE_ROOT / "gui"

HUD_PORT = 7777

# ---------------------------------------------------------------------------
# Module catalogue (name → path)
# ---------------------------------------------------------------------------

_MODULE_GROUPS: list[tuple[str, list[tuple[str, Path]]]] = [
    (
        "CORE",
        [
            ("jarvis_core", _CORE_DIR / "jarvis_core.py"),
            ("governance", _CORE_DIR / "governance.py"),
            ("config", _CORE_DIR / "config.py"),
        ],
    ),
    (
        "API",
        [
            ("web_server", _API_DIR / "web_server.py"),
            ("database", _API_DIR / "database.py"),
        ],
    ),
    (
        "GUI",
        [
            ("cyberpunk_gui", _GUI_DIR / "jarvis_gui_cyberpunk.py"),
            ("hud_server", _GUI_DIR / "hud_server.py"),
        ],
    ),
    (
        "GAME ENGINE",
        [
            ("sovereign_health", _GAME_ENGINE_DIR / "sovereign_health.py"),
            ("justice_engine", _GAME_ENGINE_DIR / "justice_engine.py"),
            ("titan_build", _GAME_ENGINE_DIR / "titan_build.py"),
            ("waveform_studio", _GAME_ENGINE_DIR / "waveform_studio.py"),
            ("soil_soul", _GAME_ENGINE_DIR / "soil_soul.py"),
            ("zero_rinse_supply", _GAME_ENGINE_DIR / "zero_rinse_supply.py"),
            ("animus_education", _GAME_ENGINE_DIR / "animus_education.py"),
            ("kinetic_transport", _GAME_ENGINE_DIR / "kinetic_transport.py"),
            ("ghost_broker", _GAME_ENGINE_DIR / "ghost_broker.py"),
            ("heart_pulse", _GAME_ENGINE_DIR / "heart_pulse.py"),
            ("lilieth_guardian", _GAME_ENGINE_DIR / "lilieth_guardian.py"),
            ("lilieth_memory", _GAME_ENGINE_DIR / "lilieth_memory.py"),
            ("mission_control", _GAME_ENGINE_DIR / "mission_control.py"),
            ("quest_viewer", _GAME_ENGINE_DIR / "quest_viewer.py"),
            ("human_state", _GAME_ENGINE_DIR / "human_state.py"),
            ("oakley_hud_bridge", _GAME_ENGINE_DIR / "oakley_hud_bridge.py"),
            ("gesture_bridge", _GAME_ENGINE_DIR / "gesture_bridge.py"),
            ("omega_integrator", _GAME_ENGINE_DIR / "omega_integrator.py"),
            ("evolution_engine", _GAME_ENGINE_DIR / "evolution_engine.py"),
            ("roi_engine", _GAME_ENGINE_DIR / "roi_engine.py"),
            ("bounty_board", _GAME_ENGINE_DIR / "bounty_board.py"),
            ("forensic_auditor", _GAME_ENGINE_DIR / "forensic_auditor.py"),
            ("frequency_shield", _GAME_ENGINE_DIR / "frequency_shield.py"),
        ],
    ),
]


def _check_modules() -> dict[str, list[dict[str, Any]]]:
    return {
        group: [{"name": name, "online": path.exists()} for name, path in modules]
        for group, modules in _MODULE_GROUPS
    }


# ---------------------------------------------------------------------------
# Live state
# ---------------------------------------------------------------------------

_human_state: dict[str, Any] = {
    "cognitive_load": 45,
    "energy_level": 78,
    "pain_flag": False,
    "volatility": "STABLE",
    "attention_index": 72,
    "sensory_load": 30,
    "exec_function": 65,
}

# Simulated biometric drift parameters
_BIO_CLOCK: float = 0.0


def _tick_biometrics() -> None:
    """
    Advance the simulated human-state metrics by one step.

    Uses slow sinusoidal drift plus small random jitter so the HUD panels
    show realistic-looking fluctuations without real sensor hardware.
    Values are clamped to sensible ranges and volatility / pain_flag are
    derived from the current cognitive load.
    """
    global _BIO_CLOCK
    _BIO_CLOCK += 0.08  # advances ~0.08 rad per 2-second broadcast tick

    def _wave(base: float, amp: float, phase: float = 0.0) -> int:
        raw = base + amp * math.sin(_BIO_CLOCK + phase) + random.uniform(-2, 2)
        return int(max(0, min(100, raw)))

    _human_state["cognitive_load"] = _wave(48, 18, 0.0)
    _human_state["energy_level"]   = _wave(70, 12, 1.6)
    _human_state["attention_index"]  = _wave(68, 15, 3.1)
    _human_state["sensory_load"]     = _wave(32, 14, 0.8)
    _human_state["exec_function"]    = _wave(63, 10, 2.4)

    cog = _human_state["cognitive_load"]
    if cog > 80:
        _human_state["volatility"] = "ELEVATED"
        _human_state["pain_flag"]  = random.random() < 0.25
    elif cog > 65:
        _human_state["volatility"] = "FLUCTUATING"
        _human_state["pain_flag"]  = False
    else:
        _human_state["volatility"] = "STABLE"
        _human_state["pain_flag"]  = False


def _get_status_payload() -> dict[str, Any]:
    return {
        "timestamp": time.time(),
        "modules": _check_modules(),
        "human_state": _human_state,
        "sovereign_freq": "10^47 Hz",
        "node": "29",
        "phase": "GENESIS 0.1",
    }


# ---------------------------------------------------------------------------
# WebSocket connection manager
# ---------------------------------------------------------------------------


class _ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._active = [c for c in self._active if c is not ws]

    async def broadcast(self, data: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._active):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


_manager = _ConnectionManager()

# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------


def _handle_command(cmd: str) -> str:
    lower = cmd.lower().strip()
    if lower in ("status", "ping"):
        return "▹ All systems nominal. Sovereign frequency locked."
    if lower in ("help", "?"):
        return "▹ Available: status | ping | node | freq | modules | help"
    if lower == "node":
        return "▹ Operating on Node 29 — The 29th Node of the Sovereign Grid."
    if lower == "freq":
        return "▹ Sovereign Frequency: 10^47 Hz — LOCKED."
    if lower == "modules":
        groups = _check_modules()
        total_on = sum(m["online"] for mods in groups.values() for m in mods)
        total_off = sum(not m["online"] for mods in groups.values() for m in mods)
        return f"▹ Modules — ONLINE: {total_on}  OFFLINE: {total_off}"
    if lower in ("shutdown", "exit", "quit"):
        return "▹ Shutdown requires physical confirmation. Type CONFIRM_SHUTDOWN."
    if lower == "confirm_shutdown":
        asyncio.get_event_loop().call_later(0.5, lambda: os._exit(0))
        return "▹ Initiating graceful shutdown..."
    return f"▹ Unknown directive: {cmd!r}. Type 'help' for available commands."


# ---------------------------------------------------------------------------
# Embedded HUD HTML
# ---------------------------------------------------------------------------

_HUD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>ENKI AI — NODE 29 HUD</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  * { font-family: 'Share Tech Mono', monospace; box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #000; overflow: hidden; height: 100%; }

  .neon-cyan   { color: #00e5ff; text-shadow: 0 0 10px #00e5ff, 0 0 20px #00e5ff44; }
  .neon-green  { color: #00ff88; text-shadow: 0 0 8px  #00ff88, 0 0 16px #00ff8844; }
  .neon-amber  { color: #ffaa00; text-shadow: 0 0 8px  #ffaa00, 0 0 16px #ffaa0044; }
  .neon-red    { color: #ff2244; text-shadow: 0 0 8px  #ff2244, 0 0 16px #ff224444; }
  .neon-purple { color: #cc44ff; text-shadow: 0 0 8px  #cc44ff; }

  .panel {
    background: rgba(0, 20, 40, 0.85);
    border: 1px solid #00e5ff22;
    backdrop-filter: blur(8px);
  }

  @keyframes scan {
    0%   { transform: translateY(-4px); }
    100% { transform: translateY(100vh); }
  }
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
  }
  @keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 6px #00e5ff33; }
    50%       { box-shadow: 0 0 22px #00e5ff88, 0 0 44px #00e5ff22; }
  }
  @keyframes freq-bar {
    0%, 100% { height: 4px; }
    50%       { height: 30px; }
  }

  .scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(to bottom, transparent, #00e5ff18, transparent);
    animation: scan 7s linear infinite;
    pointer-events: none; z-index: 9999;
  }
  .status-dot  { animation: blink 1.4s ease-in-out infinite; }
  .glow-box    { animation: glow-pulse 3s ease-in-out infinite; }

  .freq-bar {
    width: 3px; background: #00e5ff; border-radius: 2px; margin: 0 1px;
    animation: freq-bar ease-in-out infinite;
    box-shadow: 0 0 4px #00e5ff;
  }

  .module-card {
    background: rgba(0, 25, 55, 0.55);
    border: 1px solid #00e5ff18;
    transition: border-color 0.2s, background 0.2s;
  }
  .module-card:hover { border-color: #00e5ff55; background: rgba(0, 40, 80, 0.75); }
  .module-online  { border-left: 3px solid #00ff88; }
  .module-offline { border-left: 3px solid #ff2244; }

  .cmd-input {
    background: rgba(0, 8, 24, 0.9);
    border: 1px solid #00e5ff33;
    color: #00e5ff;
    outline: none;
    caret-color: #00e5ff;
  }
  .cmd-input:focus { border-color: #00e5ff; box-shadow: 0 0 10px #00e5ff22; }

  .scrollbar-custom::-webkit-scrollbar       { width: 4px; }
  .scrollbar-custom::-webkit-scrollbar-track  { background: transparent; }
  .scrollbar-custom::-webkit-scrollbar-thumb  { background: #00e5ff33; border-radius: 2px; }

  .progress-bar {
    height: 4px; border-radius: 2px;
    background: linear-gradient(to right, #00e5ff, #00ff88);
    box-shadow: 0 0 6px #00e5ff66;
    transition: width 0.6s ease;
  }
  .progress-energy {
    background: linear-gradient(to right, #00ff88, #00e5ff);
  }

  .grid-bg {
    background-image:
      linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px);
    background-size: 42px 42px;
  }
  .corner-tl { border-top: 2px solid #00e5ff; border-left: 2px solid #00e5ff; }
  .corner-tr { border-top: 2px solid #00e5ff; border-right: 2px solid #00e5ff; }
  .corner-bl { border-bottom: 2px solid #00e5ff; border-left: 2px solid #00e5ff; }
  .corner-br { border-bottom: 2px solid #00e5ff; border-right: 2px solid #00e5ff; }
</style>
</head>
<body class="h-screen w-screen text-cyan-100 grid-bg flex flex-col">

<!-- Scan Line -->
<div class="scan-line"></div>

<!-- Ambient Glow -->
<div class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full pointer-events-none"
     style="background:radial-gradient(ellipse,rgba(0,229,255,0.045) 0%,transparent 70%);"></div>

<!-- ══════════ TOP BAR ══════════ -->
<header class="flex items-center justify-between px-6 py-2 border-b border-cyan-900/40 bg-black/65 backdrop-blur-sm shrink-0 select-none">
  <div class="flex items-center gap-5">
    <div>
      <span class="text-2xl font-bold neon-cyan tracking-[0.3em]">ENKI AI</span>
      <span class="ml-3 text-[10px] text-cyan-600 border border-cyan-900 px-2 py-0.5 rounded">ADA EDITION</span>
    </div>
    <div class="text-[11px] text-cyan-600 border border-cyan-900/50 px-2 py-1 rounded">
      NODE&nbsp;<span class="neon-cyan font-bold" id="node-id">29</span>
    </div>
    <div class="text-[11px] text-cyan-600 border border-cyan-900/50 px-2 py-1 rounded">
      PHASE:&nbsp;<span class="neon-cyan font-bold" id="phase-label">GENESIS&nbsp;0.1</span>
    </div>
  </div>

  <!-- Frequency visualiser bars -->
  <div class="flex items-end h-10 gap-0.5" id="freq-viz"></div>

  <div class="flex items-center gap-5">
    <div class="text-[11px] text-cyan-600">
      FREQ:&nbsp;<span class="neon-purple font-bold" id="freq-label">10^47&nbsp;Hz</span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-2 h-2 rounded-full bg-green-400 status-dot" id="conn-dot"></div>
      <span class="text-[11px] neon-green font-bold" id="conn-status">ONLINE</span>
    </div>
    <div class="text-lg font-bold neon-cyan" id="live-clock">00:00:00</div>
  </div>
</header>

<!-- ══════════ MAIN BODY ══════════ -->
<div class="flex-1 flex overflow-hidden">

  <!-- ── LEFT: Module Status ── -->
  <aside class="w-72 flex flex-col border-r border-cyan-900/30 bg-black/25 shrink-0">
    <div class="px-4 py-2 border-b border-cyan-900/30 shrink-0">
      <span class="text-[11px] neon-cyan tracking-widest">▧ SYSTEM MODULES</span>
    </div>
    <div class="flex-1 overflow-y-auto scrollbar-custom px-3 py-2" id="modules-container">
      <div class="text-xs text-cyan-700 text-center py-8 animate-pulse">INITIALISING…</div>
    </div>
    <div class="px-4 py-2 border-t border-cyan-900/30 shrink-0 flex justify-between text-[11px]">
      <span class="text-cyan-700">ONLINE</span><span class="neon-green font-bold" id="online-count">—</span>
      <span class="text-cyan-700">OFFLINE</span><span class="neon-red font-bold" id="offline-count">—</span>
    </div>
  </aside>

  <!-- ── CENTER: Core HUD ── -->
  <main class="flex-1 flex flex-col overflow-hidden">

    <!-- Sovereignty ribbon -->
    <div class="flex items-center justify-center gap-6 py-3 border-b border-cyan-900/30 shrink-0 flex-wrap">
      <div class="text-center panel rounded px-5 py-2 glow-box">
        <div class="text-[10px] text-cyan-700 tracking-widest">SOVEREIGN FREQ</div>
        <div class="text-lg neon-purple font-bold" id="sov-freq">10^47 Hz</div>
      </div>
      <div class="text-center panel rounded px-5 py-2">
        <div class="text-[10px] text-cyan-700 tracking-widest">PROTOCOL</div>
        <div class="text-lg neon-cyan font-bold">ODIN</div>
      </div>
      <div class="text-center panel rounded px-5 py-2">
        <div class="text-[10px] text-cyan-700 tracking-widest">PILLARS</div>
        <div class="text-lg neon-green font-bold">14+1</div>
      </div>
      <div class="text-center panel rounded px-5 py-2">
        <div class="text-[10px] text-cyan-700 tracking-widest">HEARTS</div>
        <div class="text-lg neon-amber font-bold">15B</div>
      </div>
      <div class="text-center panel rounded px-5 py-2">
        <div class="text-[10px] text-cyan-700 tracking-widest">UPTIME</div>
        <div class="text-lg neon-cyan font-bold" id="uptime">00:00:00</div>
      </div>
    </div>

    <!-- Neural console -->
    <div class="flex-1 flex flex-col p-4 min-h-0 gap-3">
      <!-- Corner decorations -->
      <div class="flex-1 panel rounded-xl flex flex-col min-h-0 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-4 h-4 corner-tl rounded-tl-xl"></div>
        <div class="absolute top-0 right-0 w-4 h-4 corner-tr rounded-tr-xl"></div>
        <div class="absolute bottom-0 left-0 w-4 h-4 corner-bl rounded-bl-xl"></div>
        <div class="absolute bottom-0 right-0 w-4 h-4 corner-br rounded-br-xl"></div>
        <div class="px-5 py-2 border-b border-cyan-900/30 text-[11px] neon-cyan tracking-widest shrink-0">
          ▧ NEURAL CONSOLE
        </div>
        <div class="flex-1 overflow-y-auto scrollbar-custom p-4 space-y-0.5 min-h-0" id="console-log">
          <div class="text-xs text-cyan-700">[ INITIALISING NEURAL INTERFACE… ]</div>
        </div>
      </div>
    </div>

    <!-- Command input -->
    <div class="px-4 pb-4 shrink-0">
      <div class="panel rounded-xl p-3">
        <div class="text-[10px] text-cyan-700 mb-2 tracking-widest">▧ COMMAND INPUT</div>
        <div class="flex gap-2 items-center">
          <span class="neon-cyan text-sm shrink-0">▹</span>
          <input id="cmd-input" type="text" autocomplete="off" spellcheck="false"
                 class="cmd-input flex-1 px-3 py-2 rounded text-sm"
                 placeholder="Enter sovereign directive…" />
          <button id="cmd-btn"
                  class="px-4 py-2 text-[11px] font-bold rounded border border-cyan-500/40
                         hover:border-cyan-400 bg-cyan-950/40 hover:bg-cyan-900/50
                         neon-cyan transition-all tracking-widest shrink-0">
            TRANSMIT
          </button>
        </div>
      </div>
    </div>
  </main>

  <!-- ── RIGHT: Human State ── -->
  <aside class="w-64 flex flex-col border-l border-cyan-900/30 bg-black/25 shrink-0">
    <div class="px-4 py-2 border-b border-cyan-900/30 shrink-0">
      <span class="text-[11px] neon-cyan tracking-widest">▧ HUMAN STATE</span>
    </div>

    <div class="flex-1 p-4 space-y-4 overflow-y-auto scrollbar-custom">

      <!-- Attention Index -->
      <div>
        <div class="flex justify-between text-[11px] mb-1">
          <span class="text-cyan-700">ATTENTION INDEX</span>
          <span class="neon-cyan font-bold" id="attn-val">—</span>
        </div>
        <div class="h-1.5 bg-cyan-950 rounded-full overflow-hidden">
          <div class="progress-bar h-full" id="attn-bar" style="width:0%"></div>
        </div>
      </div>

      <!-- Sensory Load -->
      <div>
        <div class="flex justify-between text-[11px] mb-1">
          <span class="text-cyan-700">SENSORY LOAD</span>
          <span class="neon-amber font-bold" id="sensory-val">—</span>
        </div>
        <div class="h-1.5 bg-cyan-950 rounded-full overflow-hidden">
          <div class="progress-bar h-full" style="background:linear-gradient(to right,#ffaa00,#ff2244);width:0%" id="sensory-bar"></div>
        </div>
      </div>

      <!-- Executive Function -->
      <div>
        <div class="flex justify-between text-[11px] mb-1">
          <span class="text-cyan-700">EXEC FUNCTION</span>
          <span class="neon-green font-bold" id="exec-val">—</span>
        </div>
        <div class="h-1.5 bg-cyan-950 rounded-full overflow-hidden">
          <div class="progress-bar progress-energy h-full" id="exec-bar" style="width:0%"></div>
        </div>
      </div>

      <!-- Cognitive Load -->
      <div>
        <div class="flex justify-between text-[11px] mb-1">
          <span class="text-cyan-700">COGNITIVE LOAD</span>
          <span class="neon-amber font-bold" id="cog-val">—</span>
        </div>
        <div class="h-1.5 bg-cyan-950 rounded-full overflow-hidden">
          <div class="progress-bar h-full" id="cog-bar" style="width:0%"></div>
        </div>
      </div>

      <!-- Energy -->
      <div>
        <div class="flex justify-between text-[11px] mb-1">
          <span class="text-cyan-700">ENERGY LEVEL</span>
          <span class="neon-green font-bold" id="energy-val">—</span>
        </div>
        <div class="h-1.5 bg-cyan-950 rounded-full overflow-hidden">
          <div class="progress-bar progress-energy h-full" id="energy-bar" style="width:0%"></div>
        </div>
      </div>

      <!-- Volatility -->
      <div class="panel rounded-lg p-3">
        <div class="text-[10px] text-cyan-700 mb-1 tracking-widest">SOMATIC FREQUENCY</div>
        <div class="text-sm font-bold neon-green" id="volatility">STABLE</div>
      </div>

      <!-- Pain Flag -->
      <div class="panel rounded-lg p-3 flex justify-between items-center">
        <span class="text-[11px] text-cyan-700">PAIN FLAG</span>
        <span class="text-[11px] font-bold neon-green" id="pain-flag">CLEAR</span>
      </div>

      <!-- Hard Boundaries -->
      <div class="panel rounded-lg p-3">
        <div class="text-[10px] text-cyan-700 mb-2 tracking-widest">HARD BOUNDARIES</div>
        <div class="space-y-1 text-[11px]">
          <div class="neon-green">✓ No Compliance-Correction</div>
          <div class="neon-green">✓ No Gated Access</div>
          <div class="neon-green">✓ Sovereignty Active</div>
        </div>
      </div>

      <!-- Project -->
      <div class="panel rounded-lg p-3">
        <div class="text-[10px] text-cyan-700 mb-1 tracking-widest">ACTIVE PROJECT</div>
        <div class="text-sm font-bold neon-cyan" id="active-project">DEFAULT</div>
      </div>

    </div>

    <div class="px-4 py-3 border-t border-cyan-900/30 shrink-0 text-center text-[10px] text-cyan-800">
      OUSH. THE ARCHITECT HAS SPOKEN.
    </div>
  </aside>

</div><!-- /main body -->

<script>
// ─── Config ───────────────────────────────────────────────────────────────
const WS_URL = `ws://${location.host}/ws`;
const CONSOLE_MAX = 120;
const startTime = Date.now();

// ─── Freq-viz setup ────────────────────────────────────────────────────────
(function buildFreqBars() {
  const container = document.getElementById('freq-viz');
  const NUM = 22;
  for (let i = 0; i < NUM; i++) {
    const b = document.createElement('div');
    b.className = 'freq-bar';
    b.style.animationDuration = (0.5 + Math.random() * 1.2).toFixed(2) + 's';
    b.style.animationDelay   = '-' + (Math.random() * 2).toFixed(2) + 's';
    container.appendChild(b);
  }
})();

// ─── Clock / uptime ────────────────────────────────────────────────────────
function updateClock() {
  document.getElementById('live-clock').textContent =
    new Date().toLocaleTimeString([], { hour12: false });

  const s  = Math.floor((Date.now() - startTime) / 1000);
  const hh = String(Math.floor(s / 3600)).padStart(2, '0');
  const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  const el = document.getElementById('uptime');
  if (el) el.textContent = `${hh}:${mm}:${ss}`;
}
setInterval(updateClock, 1000);
updateClock();

// ─── Console log ──────────────────────────────────────────────────────────
const LOG_COLORS = {
  info:    'text-cyan-400',
  success: 'text-green-400',
  warn:    'text-amber-400',
  error:   'text-red-400',
  system:  'text-purple-400',
};

function logConsole(msg, level = 'info') {
  const el   = document.getElementById('console-log');
  const line = document.createElement('div');
  const t    = new Date().toLocaleTimeString([], { hour12: false });
  line.className   = `text-xs ${LOG_COLORS[level] || 'text-cyan-400'} leading-relaxed`;
  line.textContent = `[${t}] ${msg}`;
  el.appendChild(line);
  while (el.children.length > CONSOLE_MAX) el.removeChild(el.firstChild);
  el.scrollTop = el.scrollHeight;
}

// ─── Render modules ────────────────────────────────────────────────────────
function renderModules(data) {
  const container = document.getElementById('modules-container');
  container.innerHTML = '';
  let on = 0, off = 0;

  for (const [group, mods] of Object.entries(data)) {
    const section = document.createElement('div');
    section.innerHTML = `<div class="text-[10px] text-cyan-700 tracking-widest mt-2 mb-1">${group}</div>`;

    for (const mod of mods) {
      if (mod.online) on++; else off++;
      const card = document.createElement('div');
      card.className = `module-card rounded px-2 py-1 mb-0.5 flex justify-between items-center
                        ${mod.online ? 'module-online' : 'module-offline'}`;
      card.innerHTML = `
        <span class="text-[11px] text-cyan-300 truncate">${mod.name}</span>
        <span class="text-[10px] font-bold shrink-0 ml-2 ${mod.online ? 'neon-green' : 'neon-red'}">
          ${mod.online ? '●' : '○'}
        </span>`;
      section.appendChild(card);
    }
    container.appendChild(section);
  }

  document.getElementById('online-count').textContent  = on;
  document.getElementById('offline-count').textContent = off;
}

// ─── Render human state ────────────────────────────────────────────────────
function renderHumanState(s) {
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  const setW = (id, pct) => { const el = document.getElementById(id); if (el) el.style.width = pct + '%'; };

  set('cog-val',    s.cognitive_load + '%');
  setW('cog-bar',   s.cognitive_load);
  set('energy-val', s.energy_level + '%');
  setW('energy-bar', s.energy_level);

  if (s.attention_index !== undefined) {
    set('attn-val', s.attention_index + '%');
    setW('attn-bar', s.attention_index);
  }
  if (s.sensory_load !== undefined) {
    set('sensory-val', s.sensory_load + '%');
    setW('sensory-bar', s.sensory_load);
  }
  if (s.exec_function !== undefined) {
    set('exec-val', s.exec_function + '%');
    setW('exec-bar', s.exec_function);
  }

  const volEl = document.getElementById('volatility');
  if (volEl) {
    volEl.textContent  = s.volatility;
    volEl.className    = `text-sm font-bold ${s.volatility === 'STABLE' ? 'neon-green' : s.volatility === 'ELEVATED' ? 'neon-red' : 'neon-amber'}`;
  }
  const painEl = document.getElementById('pain-flag');
  if (painEl) {
    painEl.textContent = s.pain_flag ? 'ACTIVE' : 'CLEAR';
    painEl.className   = `text-[11px] font-bold ${s.pain_flag ? 'neon-red' : 'neon-green'}`;
  }
}

// ─── WebSocket ─────────────────────────────────────────────────────────────
let ws, reconnectTimer;

function setConnStatus(text, cls) {
  document.getElementById('conn-status').textContent = text;
  document.getElementById('conn-status').className   = `text-[11px] font-bold ${cls}`;
}

function connectWS() {
  logConsole('Connecting to ENKI core…', 'system');
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setConnStatus('ONLINE', 'neon-green');
    logConsole('Neural interface established.', 'success');
    clearTimeout(reconnectTimer);
  };

  ws.onmessage = (e) => {
    try {
      const d = JSON.parse(e.data);
      if (d.modules)       renderModules(d.modules);
      if (d.human_state)   renderHumanState(d.human_state);
      if (d.sovereign_freq) {
        document.getElementById('sov-freq').textContent   = d.sovereign_freq;
        document.getElementById('freq-label').textContent = d.sovereign_freq;
      }
      if (d.node)  document.getElementById('node-id').textContent     = d.node;
      if (d.phase) document.getElementById('phase-label').textContent  = d.phase;
      if (d.message) logConsole(d.message, d.level || 'info');
    } catch (err) {
      console.error('WS parse error', err);
    }
  };

  ws.onclose = () => {
    setConnStatus('RECONNECTING', 'neon-amber');
    logConsole('Connection lost. Reconnecting in 3 s…', 'warn');
    reconnectTimer = setTimeout(connectWS, 3000);
  };

  ws.onerror = () => logConsole('WebSocket error.', 'error');
}

// ─── Command submit ─────────────────────────────────────────────────────────
function submitCommand() {
  const input = document.getElementById('cmd-input');
  const cmd   = input.value.trim();
  if (!cmd) return;
  logConsole(`▹ ${cmd}`, 'info');
  input.value = '';
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'command', text: cmd }));
  } else {
    logConsole('✗ Not connected to core.', 'error');
  }
}

document.getElementById('cmd-btn').addEventListener('click', submitCommand);
document.getElementById('cmd-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') submitCommand();
});

// ─── Boot ───────────────────────────────────────────────────────────────────
logConsole('[ ENKI AI — NODE 29 SOVEREIGN HUD ]', 'system');
logConsole('[ SOVEREIGN FREQUENCY: 10^47 Hz LOCKED ]', 'system');
logConsole('[ ODIN PROTOCOL: ACTIVE ]', 'system');
logConsole('[ 14+1 PILLAR GOVERNANCE MODEL: ENGAGED ]', 'system');
logConsole('[ AWAITING NEURAL HANDSHAKE… ]', 'system');
connectWS();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="Enki AI HUD", docs_url=None, redoc_url=None)


@app.get("/", response_class=HTMLResponse)
async def get_hud() -> HTMLResponse:
    return HTMLResponse(_HUD_HTML)


@app.get("/api/status")
async def api_status() -> dict[str, Any]:
    return _get_status_payload()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await _manager.connect(ws)
    log.info("HUD client connected from %s", ws.client)
    try:
        # Send full state immediately on connect
        await ws.send_json(
            {
                **_get_status_payload(),
                "message": "ENKI AI Node 29 — all systems loaded to Oakley Bridge.",
                "level": "success",
            }
        )
        # Relay commands; broadcast status updates every 2 seconds
        while True:
            try:
                raw = await asyncio.wait_for(ws.receive_text(), timeout=2.0)
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if data.get("type") == "command":
                    cmd = str(data.get("text", "")).strip()
                    log.info("HUD command: %s", cmd)
                    reply = _handle_command(cmd)
                    await ws.send_json({"message": reply, "level": "success"})
            except asyncio.TimeoutError:
                _tick_biometrics()
                await _manager.broadcast(_get_status_payload())
    except WebSocketDisconnect:
        _manager.disconnect(ws)
        log.info("HUD client disconnected")
    except Exception as exc:
        log.warning("WS session error: %s", exc)
        _manager.disconnect(ws)


# ---------------------------------------------------------------------------
# Public launch helper
# ---------------------------------------------------------------------------


def run(
    host: str = "127.0.0.1",
    port: int = HUD_PORT,
    open_browser: bool = True,
) -> None:
    """Start the HUD server.  Optionally opens the browser automatically."""
    if open_browser:
        import threading
        import webbrowser

        def _open() -> None:
            time.sleep(1.2)
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
    log.info("Starting Enki AI Sovereign HUD on http://127.0.0.1:%d", HUD_PORT)
    run()
