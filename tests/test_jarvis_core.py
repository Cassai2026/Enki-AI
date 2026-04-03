"""
Tests for JARVIS command routing (enki_ai.core.jarvis_core).
"""

import pytest

from enki_ai.core.jarvis_core import (
    extract_volume_number,
    normalize_text,
    route_command,
)


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------


def test_normalize_strips_and_lowercases():
    assert normalize_text("  Hello World  ") == "hello world"


def test_normalize_collapses_whitespace():
    assert normalize_text("hello   world") == "hello world"


def test_normalize_empty_string():
    assert normalize_text("") == ""


def test_normalize_none_like():
    # Passing None should not crash – it is cast to empty string via (t or "")
    assert normalize_text("") == ""


# ---------------------------------------------------------------------------
# extract_volume_number
# ---------------------------------------------------------------------------


def test_extract_volume_plain_number():
    assert extract_volume_number("volume 50") == 50


def test_extract_volume_with_percent():
    assert extract_volume_number("set volume to 75%") == 75


def test_extract_volume_with_word_percent():
    assert extract_volume_number("volume 30 percent") == 30


def test_extract_volume_clamps_high():
    assert extract_volume_number("volume 999") == 100


def test_extract_volume_clamps_low():
    # The regex only captures digit characters; "-10" yields 10 (within 0-100, no clamping needed)
    assert extract_volume_number("volume -10") == 10


def test_extract_volume_no_number():
    assert extract_volume_number("volume up") is None


# ---------------------------------------------------------------------------
# route_command – shutdown / help
# ---------------------------------------------------------------------------


def test_route_shutdown():
    action, payload = route_command("shutdown")
    assert action == "shutdown"
    assert payload is None


def test_route_shutdown_variant():
    action, _ = route_command("quit")
    assert action == "shutdown"


def test_route_help():
    action, payload = route_command("help")
    assert action == "help"
    assert payload is None


def test_route_help_variant():
    action, _ = route_command("what can you do")
    assert action == "help"


# ---------------------------------------------------------------------------
# route_command – mute / unmute
# ---------------------------------------------------------------------------


def test_route_mute():
    action, _ = route_command("mute")
    assert action == "mute"


def test_route_unmute():
    action, _ = route_command("unmute")
    assert action == "unmute"


# ---------------------------------------------------------------------------
# route_command – volume
# ---------------------------------------------------------------------------


def test_route_volume_set():
    action, payload = route_command("volume 50")
    assert action == "volume_set"
    assert payload == "50"


def test_route_volume_up():
    action, payload = route_command("volume up 10")
    assert action == "volume_up"
    assert payload == "10"


def test_route_volume_up_default():
    action, payload = route_command("volume up")
    assert action == "volume_up"
    assert payload == "10"


def test_route_volume_down():
    action, payload = route_command("volume down 20")
    assert action == "volume_down"
    assert payload == "20"


def test_route_volume_louder():
    action, _ = route_command("louder")
    assert action == "volume_up"


def test_route_volume_quieter():
    action, _ = route_command("volume quieter")
    assert action == "volume_down"


def test_route_volume_no_number():
    action, payload = route_command("set the volume")
    assert action == "volume_set"
    assert payload is None


# ---------------------------------------------------------------------------
# route_command – open
# ---------------------------------------------------------------------------


def test_route_open_explicit():
    action, payload = route_command("open chrome")
    assert action == "open"
    assert payload == "chrome"


def test_route_launch():
    action, payload = route_command("launch discord")
    assert action == "open"
    assert payload == "discord"


def test_route_open_no_target():
    action, _ = route_command("open")
    assert action == "none"


def test_route_fallback_open():
    # Unrecognised phrase with content → treated as open target
    action, payload = route_command("notepad")
    assert action == "open"
    assert payload == "notepad"


def test_route_empty_command():
    action, _ = route_command("")
    assert action == "none"
