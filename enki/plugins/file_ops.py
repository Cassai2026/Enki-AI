"""File-operations plugin — read / write / list files safely."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from enki.plugins.base import Plugin, PluginResult

# Restrict access to the current working directory by default.
_MAX_READ_BYTES = 1024 * 1024  # 1 MiB


def _safe_path(raw: str) -> Path:
    """Resolve path and ensure it stays inside cwd."""
    cwd = Path.cwd().resolve()
    target = (cwd / raw).resolve()
    if not str(target).startswith(str(cwd)):
        raise PermissionError(f"Access outside working directory is not allowed: {raw!r}")
    return target


class FileReadPlugin(Plugin):
    """Read the contents of a file."""

    @property
    def name(self) -> str:
        return "file_read"

    @property
    def description(self) -> str:
        return "Read and return the text contents of a file at the given path."

    def parameters(self) -> dict:
        return {
            "path": {"type": "string", "description": "Relative path to the file."},
        }

    async def run(self, path: str, **_: Any) -> PluginResult:
        try:
            p = _safe_path(path)
            if not p.is_file():
                return PluginResult(success=False, output={"error": f"Not a file: {path!r}"})
            content = p.read_bytes()
            if len(content) > _MAX_READ_BYTES:
                return PluginResult(
                    success=False,
                    output={"error": f"File too large (>{_MAX_READ_BYTES} bytes)"},
                )
            return PluginResult(success=True, output={"path": path, "content": content.decode("utf-8", errors="replace")})
        except PermissionError as exc:
            return PluginResult(success=False, output={"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            return PluginResult(success=False, output={"error": str(exc)})


class FileWritePlugin(Plugin):
    """Write text to a file (creates or overwrites)."""

    @property
    def name(self) -> str:
        return "file_write"

    @property
    def description(self) -> str:
        return "Write text content to a file, creating it if it does not exist."

    def parameters(self) -> dict:
        return {
            "path": {"type": "string", "description": "Relative path to the file."},
            "content": {"type": "string", "description": "Text content to write."},
        }

    async def run(self, path: str, content: str, **_: Any) -> PluginResult:
        try:
            p = _safe_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return PluginResult(success=True, output={"path": path, "bytes_written": len(content.encode())})
        except PermissionError as exc:
            return PluginResult(success=False, output={"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            return PluginResult(success=False, output={"error": str(exc)})


class FileListPlugin(Plugin):
    """List files in a directory."""

    @property
    def name(self) -> str:
        return "file_list"

    @property
    def description(self) -> str:
        return "List the files and directories inside a given directory path."

    def parameters(self) -> dict:
        return {
            "path": {
                "type": "string",
                "description": "Relative path to the directory. Use '.' for current directory.",
            },
        }

    async def run(self, path: str = ".", **_: Any) -> PluginResult:
        try:
            p = _safe_path(path)
            if not p.is_dir():
                return PluginResult(success=False, output={"error": f"Not a directory: {path!r}"})
            entries = sorted(
                [{"name": e.name, "type": "dir" if e.is_dir() else "file", "size": e.stat().st_size if e.is_file() else None}
                 for e in p.iterdir()],
                key=lambda x: x["name"],
            )
            return PluginResult(success=True, output={"path": path, "entries": entries})
        except PermissionError as exc:
            return PluginResult(success=False, output={"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            return PluginResult(success=False, output={"error": str(exc)})
