"""Plugins package — built-in tools."""
from enki.plugins.base import Plugin, PluginResult
from enki.plugins.calculator import CalculatorPlugin
from enki.plugins.web_search import WebSearchPlugin
from enki.plugins.file_ops import FileReadPlugin, FileWritePlugin, FileListPlugin

DEFAULT_PLUGINS: list[Plugin] = [
    CalculatorPlugin(),
    WebSearchPlugin(),
    FileReadPlugin(),
    FileWritePlugin(),
    FileListPlugin(),
]

__all__ = [
    "Plugin",
    "PluginResult",
    "CalculatorPlugin",
    "WebSearchPlugin",
    "FileReadPlugin",
    "FileWritePlugin",
    "FileListPlugin",
    "DEFAULT_PLUGINS",
]
