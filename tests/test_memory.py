"""Unit tests for ConversationMemory."""
import pytest

from enki.core.memory import ConversationMemory, Message


def test_empty_memory_has_no_messages():
    mem = ConversationMemory()
    assert mem.messages() == []
    assert len(mem) == 0


def test_system_prompt_prepended():
    mem = ConversationMemory()
    mem.set_system("You are a helpful assistant.")
    mem.add("user", "Hello")
    msgs = mem.messages()
    assert msgs[0].role == "system"
    assert msgs[1].role == "user"


def test_window_truncation():
    mem = ConversationMemory(window=4)
    for i in range(10):
        mem.add("user", f"msg {i}")
    assert len(mem) == 4
    # The last four messages should be kept.
    contents = [m.content for m in mem.messages()]
    assert "msg 9" in contents
    assert "msg 0" not in contents


def test_unlimited_window_keeps_all():
    mem = ConversationMemory(window=0)
    for i in range(50):
        mem.add("user", f"msg {i}")
    assert len(mem) == 50


def test_as_dicts_format():
    mem = ConversationMemory()
    mem.set_system("sys")
    mem.add("user", "hi")
    mem.add("assistant", "hello")
    dicts = mem.as_dicts()
    assert dicts == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_clear_removes_turns_but_not_system():
    mem = ConversationMemory()
    mem.set_system("sys")
    mem.add("user", "hi")
    mem.clear()
    assert len(mem) == 0
    msgs = mem.messages()
    assert len(msgs) == 1
    assert msgs[0].role == "system"


def test_tool_message_with_name():
    mem = ConversationMemory()
    mem.add("tool", '{"result": 42}', name="calculator")
    d = mem.as_dicts()[0]
    assert d["name"] == "calculator"
