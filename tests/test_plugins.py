"""Unit tests for built-in plugins."""
import pytest

from enki.plugins.calculator import CalculatorPlugin
from enki.plugins.file_ops import FileListPlugin, FileReadPlugin, FileWritePlugin


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_calculator_basic_arithmetic():
    calc = CalculatorPlugin()
    result = await calc.run(expression="2 + 2")
    assert result.success
    assert result.output["result"] == 4


@pytest.mark.asyncio
async def test_calculator_trig():
    import math

    calc = CalculatorPlugin()
    result = await calc.run(expression="round(sin(pi/2), 6)")
    assert result.success
    assert result.output["result"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_calculator_invalid_expression():
    calc = CalculatorPlugin()
    result = await calc.run(expression="import os")
    assert not result.success
    assert "error" in result.output


@pytest.mark.asyncio
async def test_calculator_power():
    calc = CalculatorPlugin()
    result = await calc.run(expression="2 ** 10")
    assert result.success
    assert result.output["result"] == 1024


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_file_write_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    writer = FileWritePlugin()
    reader = FileReadPlugin()

    write_result = await writer.run(path="hello.txt", content="Hello, Enki!")
    assert write_result.success

    read_result = await reader.run(path="hello.txt")
    assert read_result.success
    assert read_result.output["content"] == "Hello, Enki!"


@pytest.mark.asyncio
async def test_file_read_nonexistent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reader = FileReadPlugin()
    result = await reader.run(path="nope.txt")
    assert not result.success
    assert "error" in result.output


@pytest.mark.asyncio
async def test_file_list(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    lister = FileListPlugin()
    result = await lister.run(path=".")
    assert result.success
    names = {e["name"] for e in result.output["entries"]}
    assert "a.txt" in names
    assert "b.txt" in names


@pytest.mark.asyncio
async def test_file_ops_path_traversal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reader = FileReadPlugin()
    result = await reader.run(path="../../etc/passwd")
    assert not result.success
    assert "error" in result.output


# ---------------------------------------------------------------------------
# Plugin schema
# ---------------------------------------------------------------------------


def test_calculator_schema():
    calc = CalculatorPlugin()
    schema = calc.schema()
    assert schema["name"] == "calculator"
    assert "parameters" in schema
    assert "expression" in schema["parameters"]["properties"]
