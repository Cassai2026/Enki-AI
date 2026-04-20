"""
Tests for enki_ai.core.agent_loader — lazy-loading agent registry.
"""

import pytest

from enki_ai.core.agent_loader import AgentLoader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_loader() -> AgentLoader:
    """Return a fresh loader with no built-in agents (clean slate for tests)."""
    loader = AgentLoader()
    loader._registry.clear()
    loader._cache.clear()
    return loader


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_decorator_adds_to_registry():
    loader = _make_loader()

    @loader.register("my_agent")
    def _factory():
        return {"type": "my_agent"}

    assert "my_agent" in loader.available_agents()


def test_register_module_adds_to_registry():
    loader = _make_loader()
    loader.register_module("config_mod", "enki_ai.core.config")
    assert "config_mod" in loader.available_agents()


# ---------------------------------------------------------------------------
# Lazy loading
# ---------------------------------------------------------------------------


def test_get_loads_agent_on_first_call():
    loader = _make_loader()

    call_count = {"n": 0}

    @loader.register("counter")
    def _factory():
        call_count["n"] += 1
        return {"loaded": True}

    assert not loader.is_loaded("counter")
    result = loader.get("counter")
    assert result == {"loaded": True}
    assert loader.is_loaded("counter")


def test_get_caches_agent_across_calls():
    loader = _make_loader()

    call_count = {"n": 0}

    @loader.register("cached")
    def _factory():
        call_count["n"] += 1
        return object()

    obj1 = loader.get("cached")
    obj2 = loader.get("cached")
    assert obj1 is obj2, "Second call should return the same cached instance"
    assert call_count["n"] == 1, "Factory should only be called once"


def test_force_reload_creates_new_instance():
    loader = _make_loader()

    instances = []

    @loader.register("fresh")
    def _factory():
        obj = object()
        instances.append(obj)
        return obj

    first = loader.get("fresh")
    second = loader.get("fresh", force_reload=True)
    assert first is not second
    assert len(instances) == 2


def test_get_raises_key_error_for_unknown_agent():
    loader = _make_loader()
    with pytest.raises(KeyError, match="not_registered"):
        loader.get("not_registered")


def test_get_optional_returns_none_for_unknown():
    loader = _make_loader()
    result = loader.get_optional("no_such_agent")
    assert result is None


def test_get_optional_returns_none_on_factory_error():
    loader = _make_loader()

    @loader.register("broken")
    def _factory():
        raise RuntimeError("factory exploded")

    result = loader.get_optional("broken")
    assert result is None


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------


def test_available_agents_returns_sorted_list():
    loader = _make_loader()
    loader.register_module("zebra", "enki_ai.core.config")
    loader.register_module("apple", "enki_ai.core.config")
    agents = loader.available_agents()
    assert agents == sorted(agents)


def test_loaded_agents_only_shows_loaded():
    loader = _make_loader()

    @loader.register("alpha")
    def _fa():
        return "a"

    @loader.register("beta")
    def _fb():
        return "b"

    assert loader.loaded_agents() == []
    loader.get("alpha")
    assert loader.loaded_agents() == ["alpha"]
    loader.get("beta")
    assert sorted(loader.loaded_agents()) == ["alpha", "beta"]


def test_is_loaded_reflects_state():
    loader = _make_loader()

    @loader.register("target")
    def _f():
        return 42

    assert not loader.is_loaded("target")
    loader.get("target")
    assert loader.is_loaded("target")


# ---------------------------------------------------------------------------
# Memory management
# ---------------------------------------------------------------------------


def test_unload_removes_from_cache():
    loader = _make_loader()

    @loader.register("removable")
    def _f():
        return "instance"

    loader.get("removable")
    assert loader.is_loaded("removable")
    removed = loader.unload("removable")
    assert removed is True
    assert not loader.is_loaded("removable")


def test_unload_returns_false_when_not_loaded():
    loader = _make_loader()
    loader.register_module("never_loaded", "enki_ai.core.config")
    result = loader.unload("never_loaded")
    assert result is False


def test_unload_all_clears_cache():
    loader = _make_loader()

    @loader.register("a")
    def _fa():
        return 1

    @loader.register("b")
    def _fb():
        return 2

    loader.get("a")
    loader.get("b")
    count = loader.unload_all()
    assert count == 2
    assert loader.loaded_agents() == []


# ---------------------------------------------------------------------------
# Repr
# ---------------------------------------------------------------------------


def test_repr_contains_counts():
    loader = _make_loader()

    @loader.register("x")
    def _f():
        return None

    loader.get("x")
    r = repr(loader)
    assert "registered=1" in r
    assert "loaded=1" in r


# ---------------------------------------------------------------------------
# Integration: load a real lightweight module via register_module
# ---------------------------------------------------------------------------


def test_load_real_module_via_register_module():
    loader = _make_loader()
    loader.register_module("config", "enki_ai.core.config")
    cfg = loader.get("config")
    # Verify it's the real config module
    assert hasattr(cfg, "WAKE_WORD")
    assert hasattr(cfg, "PIPER_EXE")
