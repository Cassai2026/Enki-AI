"""Web-search plugin — uses DuckDuckGo Instant-Answer API (no key needed)."""
from __future__ import annotations

from typing import Any

import httpx

from enki.plugins.base import Plugin, PluginResult

_DDG_URL = "https://api.duckduckgo.com/"


class WebSearchPlugin(Plugin):
    """Search the web via DuckDuckGo Instant Answer API."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information and return a concise summary."
            " Use when the user asks about recent events, facts, or anything"
            " that might require up-to-date information."
        )

    def parameters(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "The search query.",
            },
        }

    async def run(self, query: str, **_: Any) -> PluginResult:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    _DDG_URL,
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                resp.raise_for_status()
                data = resp.json()

            abstract = data.get("AbstractText") or data.get("Answer") or ""
            related = [
                {"title": r["Text"], "url": r["FirstURL"]}
                for r in data.get("RelatedTopics", [])[:5]
                if isinstance(r, dict) and r.get("Text")
            ]

            if not abstract and not related:
                return PluginResult(
                    success=True,
                    output={"query": query, "summary": "No instant answer found.", "results": []},
                )

            return PluginResult(
                success=True,
                output={"query": query, "summary": abstract, "results": related},
            )
        except Exception as exc:  # noqa: BLE001
            return PluginResult(success=False, output={"error": str(exc), "query": query})
