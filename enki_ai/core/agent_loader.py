"""
enki_ai.core.agent_loader
=========================
Lazy-loading agent registry for Enki-AI.

Each AI agent is only imported and initialised when it is first requested.
This keeps the base memory footprint tiny and allows Enki to "cloud-load"
specialised agents on the fly — exactly the design needed for a Linux-based
OS where each agent runs as a separate, lightweight process.

Usage
-----
::

    from enki_ai.core.agent_loader import agent_loader

    # Load (or retrieve cached) the sovereign brain
    brain = agent_loader.get("sovereign_brain")

    # Check which agents are loaded right now
    print(agent_loader.loaded_agents())

    # Unload an agent to free memory
    agent_loader.unload("sovereign_brain")

Registering custom agents
-------------------------
::

    @agent_loader.register("my_agent")
    def _build_my_agent():
        from my_package.my_module import MyAgent
        return MyAgent()

"""

from __future__ import annotations

import importlib
import logging
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in agent definitions
# ---------------------------------------------------------------------------
# Each entry maps a friendly name to a factory callable that returns the
# agent instance.  Factories are called lazily — only when first requested.

_BUILTIN_AGENTS: dict[str, Callable[[], Any]] = {}


def _make_builtin(name: str, factory: Callable[[], Any]) -> None:
    _BUILTIN_AGENTS[name] = factory


# SovereignBrain — Gemini LLM engine
def _build_sovereign_brain() -> Any:
    from enki_ai.core.sovereign_brain import SovereignBrain  # type: ignore[import]
    return SovereignBrain()


# REST API (Flask)
def _build_api() -> Any:
    from enki_ai.api.web_server import app  # type: ignore[import]
    return app


# HUD server (FastAPI/WebSocket)
def _build_hud() -> Any:
    from enki_ai.gui.hud_server import app as hud_app  # type: ignore[import]
    return hud_app


# JARVIS voice core
def _build_jarvis_core() -> Any:
    import enki_ai.core.jarvis_core as jc  # type: ignore[import]
    return jc


# Sovereign Shell (menu-driven CLI)
def _build_shell() -> Any:
    from enki_ai.core.shell import SovereignShell  # type: ignore[import]
    return SovereignShell()


_make_builtin("sovereign_brain", _build_sovereign_brain)
_make_builtin("api", _build_api)
_make_builtin("hud", _build_hud)
_make_builtin("jarvis_core", _build_jarvis_core)
_make_builtin("shell", _build_shell)


# ---------------------------------------------------------------------------
# AgentLoader
# ---------------------------------------------------------------------------


class AgentLoader:
    """
    Central registry that lazily instantiates and caches AI agents.

    Parameters
    ----------
    auto_unload_unused : bool
        If ``True``, calling :meth:`unload` removes the cached instance so
        memory can be reclaimed.  Defaults to ``False`` (instances are kept
        for fast repeated access).
    """

    def __init__(self, auto_unload_unused: bool = False) -> None:
        self._registry: dict[str, Callable[[], Any]] = dict(_BUILTIN_AGENTS)
        self._cache: dict[str, Any] = {}
        self.auto_unload_unused = auto_unload_unused

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, name: str) -> Callable[[Callable[[], Any]], Callable[[], Any]]:
        """Decorator to register a factory function under *name*."""

        def decorator(factory: Callable[[], Any]) -> Callable[[], Any]:
            self._registry[name] = factory
            log.debug("[AgentLoader] Registered agent: %s", name)
            return factory

        return decorator

    def register_module(self, name: str, module_path: str, attr: str = "") -> None:
        """
        Register an agent by Python import path.

        Parameters
        ----------
        name        : friendly agent name used in :meth:`get`.
        module_path : dotted module path, e.g. ``"enki_ai.game_engine.vortex_engine"``.
        attr        : attribute on the module to use as the agent object.
                      If empty, the whole module is returned.
        """

        def factory() -> Any:
            mod = importlib.import_module(module_path)
            return getattr(mod, attr) if attr else mod

        self._registry[name] = factory
        log.debug("[AgentLoader] Registered module agent: %s -> %s.%s", name, module_path, attr)

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, name: str, *, force_reload: bool = False) -> Any:
        """
        Return the agent instance for *name*, loading it if necessary.

        Parameters
        ----------
        name         : Agent name as registered (e.g. ``"sovereign_brain"``).
        force_reload : If ``True``, discard any cached instance and re-create.

        Raises
        ------
        KeyError
            If *name* is not in the registry.
        """
        if name not in self._registry:
            raise KeyError(
                f"Agent '{name}' is not registered. "
                f"Available agents: {sorted(self._registry)}"
            )

        if force_reload and name in self._cache:
            log.info("[AgentLoader] Force-reloading agent: %s", name)
            del self._cache[name]

        if name not in self._cache:
            log.info("[AgentLoader] Loading agent: %s", name)
            try:
                self._cache[name] = self._registry[name]()
                log.info("[AgentLoader] Agent ready: %s", name)
            except Exception as exc:
                log.error("[AgentLoader] Failed to load agent '%s': %s", name, exc)
                raise

        return self._cache[name]

    def get_optional(self, name: str) -> Optional[Any]:
        """Like :meth:`get` but returns ``None`` instead of raising on error."""
        try:
            return self.get(name)
        except (KeyError, Exception) as exc:
            log.warning("[AgentLoader] Optional agent '%s' unavailable: %s", name, exc)
            return None

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def available_agents(self) -> list[str]:
        """Return sorted list of all registered agent names."""
        return sorted(self._registry)

    def loaded_agents(self) -> list[str]:
        """Return sorted list of agent names that are currently loaded in memory."""
        return sorted(self._cache)

    def is_loaded(self, name: str) -> bool:
        """Return ``True`` if *name* is currently loaded in memory."""
        return name in self._cache

    # ------------------------------------------------------------------
    # Memory management
    # ------------------------------------------------------------------

    def unload(self, name: str) -> bool:
        """
        Remove a cached agent instance from memory.

        Returns ``True`` if the agent was loaded and has been removed,
        ``False`` if it was not loaded.
        """
        if name in self._cache:
            del self._cache[name]
            log.info("[AgentLoader] Unloaded agent: %s", name)
            return True
        return False

    def unload_all(self) -> int:
        """Unload every cached agent.  Returns the number of agents removed."""
        count = len(self._cache)
        self._cache.clear()
        log.info("[AgentLoader] Unloaded all %d agents.", count)
        return count

    def __repr__(self) -> str:
        return (
            f"AgentLoader("
            f"registered={len(self._registry)}, "
            f"loaded={len(self._cache)})"
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

agent_loader: AgentLoader = AgentLoader()
