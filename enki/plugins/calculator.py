"""Calculator plugin — safe arithmetic evaluation."""
from __future__ import annotations

import math
import operator
from typing import Any

from enki.plugins.base import Plugin, PluginResult

# Safe names available inside expressions
_SAFE_GLOBALS: dict[str, Any] = {
    "__builtins__": {},
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
    "inf": math.inf,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
}


class CalculatorPlugin(Plugin):
    """Evaluate mathematical expressions safely."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Evaluate a mathematical expression and return the numeric result."
            " Supports arithmetic, trigonometry, logarithms, and more."
        )

    def parameters(self) -> dict:
        return {
            "expression": {
                "type": "string",
                "description": (
                    "A Python-syntax math expression, e.g. '2 ** 10' or 'sin(pi/2)'."
                ),
            }
        }

    async def run(self, expression: str, **_: Any) -> PluginResult:
        try:
            result = eval(expression, _SAFE_GLOBALS, {})  # noqa: S307
            return PluginResult(success=True, output={"result": result, "expression": expression})
        except Exception as exc:  # noqa: BLE001
            return PluginResult(success=False, output={"error": str(exc), "expression": expression})
