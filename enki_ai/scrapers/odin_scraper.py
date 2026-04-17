"""
ODIN Website Scraper — scrapes cassai.co.uk for quick info retrieval.

Caches pages locally (1-hour TTL).  Stores scraped data in the JARVIS
database.  Also supports parsing exported AI conversation files.
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import]
from bs4 import BeautifulSoup  # type: ignore[import]

from enki_ai.api.database import db
from enki_ai.core import config

log = logging.getLogger(__name__)

_ODIN_CACHE_DIR = str(config.PROJECT_ROOT / "data" / "odin_cache")


class OdinScraper:
    """Scrapes and caches cassai.co.uk content for ODIN/JARVIS lookups."""

    def __init__(
        self,
        base_url: str = "https://www.cassai.co.uk",
        cache_dir: str = _ODIN_CACHE_DIR,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "site_cache.json")
        self.cache: Dict[str, dict] = {}
        self._cache_max_age = timedelta(hours=1)
        os.makedirs(cache_dir, exist_ok=True)
        self._load_cache()

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def _load_cache(self) -> None:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, encoding="utf-8") as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def _save_cache(self) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)

    def _is_fresh(self, url: str) -> bool:
        if url not in self.cache:
            return False
        cached_time = datetime.fromisoformat(self.cache[url]["timestamp"])
        return datetime.now() - cached_time < self._cache_max_age

    # ------------------------------------------------------------------
    # Web scraping
    # ------------------------------------------------------------------

    def fetch_page(self, path: str = "/") -> Optional[dict]:
        """Fetch a page from cassai.co.uk; return parsed data dict."""
        url = f"{self.base_url}{path}"

        if self._is_fresh(url):
            log.debug("Cache hit: %s", url)
            return self.cache[url]["data"]

        log.info("Scraping: %s", url)
        try:
            resp = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "ODIN-Scraper/1.0 (CassAI Internal)"},
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.error("Error fetching %s: %s", url, exc)
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        page_data: Dict[str, Any] = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "headings": [h.get_text(strip=True) for h in soup.find_all(re.compile(r"^h[1-3]$"))],
            "text": soup.get_text(separator="\n", strip=True)[:5000],
            "links": [
                {"text": a.get_text(strip=True), "href": a.get("href", "")}
                for a in soup.find_all("a", href=True)
                if a.get("href", "").startswith(("/", "http"))
            ][:50],
            "meta": {
                meta.get("name", meta.get("property", "")): meta.get("content", "")
                for meta in soup.find_all("meta")
                if meta.get("content")
            },
            "scraped_at": datetime.now().isoformat(),
        }

        self.cache[url] = {"timestamp": datetime.now().isoformat(), "data": page_data}
        self._save_cache()
        db.add_data("odin_scrape", url, json.dumps(page_data))
        return page_data

    def discover_pages(self) -> List[str]:
        """Scrape the homepage and collect all internal link paths."""
        homepage = self.fetch_page("/")
        if not homepage:
            return ["/"]

        paths: set = set()
        for link in homepage.get("links", []):
            href = link.get("href", "")
            if href.startswith("/") and not href.startswith("//"):
                paths.add(href)
            elif href.startswith(self.base_url):
                paths.add(href.replace(self.base_url, ""))
        paths.add("/")
        found = sorted(paths)
        log.info("Discovered %d pages.", len(found))
        return found

    def scrape_all(self) -> List[dict]:
        """Discover and scrape all pages on cassai.co.uk."""
        paths = self.discover_pages()
        return [page for path in paths if (page := self.fetch_page(path))]

    # ------------------------------------------------------------------
    # Conversation file parser
    # ------------------------------------------------------------------

    def parse_conversation_file(self, filepath: str) -> Optional[dict]:
        """
        Parse an exported AI conversation file (.txt, .md, or .json).

        Returns a dict with keys: source, messages, message_count, parsed_at
        """
        if not os.path.exists(filepath):
            log.error("File not found: %s", filepath)
            return None

        log.info("Parsing conversation: %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            raw = f.read()

        ext = os.path.splitext(filepath)[1].lower()
        messages = self._parse_json_convo(raw) if ext == ".json" else self._parse_text_convo(raw)

        convo_data = {
            "source": os.path.basename(filepath),
            "filepath": os.path.abspath(filepath),
            "messages": messages,
            "message_count": len(messages),
            "parsed_at": datetime.now().isoformat(),
        }

        cache_key = f"file://{os.path.abspath(filepath)}"
        self.cache[cache_key] = {"timestamp": datetime.now().isoformat(), "data": convo_data}
        self._save_cache()
        db.add_data("odin_convo", cache_key, json.dumps(convo_data))
        log.info("Parsed %d messages from %s", len(messages), filepath)
        return convo_data

    def _parse_text_convo(self, raw: str) -> List[dict]:
        """Parse a plain text or markdown conversation into message dicts."""
        messages: List[dict] = []
        current_role: Optional[str] = None
        current_lines: List[str] = []

        role_patterns = [
            (re.compile(r"^(?:User|You|Human|Me)\s*[:\-]", re.IGNORECASE), "user"),
            (re.compile(r"^(?:AI|Assistant|Bot|Gemini|ChatGPT|Copilot|ODIN)\s*[:\-]", re.IGNORECASE), "assistant"),
            (re.compile(r"^>\s"), "assistant"),
            (re.compile(r"^\*\*(?:User|You|Human)\*\*", re.IGNORECASE), "user"),
            (re.compile(r"^\*\*(?:AI|Assistant|Gemini|ChatGPT)\*\*", re.IGNORECASE), "assistant"),
        ]

        for line in raw.split("\n"):
            stripped = line.strip()
            if not stripped:
                if current_lines:
                    current_lines.append("")
                continue

            detected_role: Optional[str] = None
            clean_line = stripped
            for pattern, role in role_patterns:
                match = pattern.match(stripped)
                if match:
                    detected_role = role
                    clean_line = stripped[match.end():].strip()
                    break

            if detected_role and detected_role != current_role:
                if current_role and current_lines:
                    messages.append({"role": current_role, "content": "\n".join(current_lines).strip()})
                current_role = detected_role
                current_lines = [clean_line] if clean_line else []
            else:
                if current_role is None:
                    current_role = "user"
                current_lines.append(stripped)

        if current_role and current_lines:
            messages.append({"role": current_role, "content": "\n".join(current_lines).strip()})
        return messages

    def _parse_json_convo(self, raw: str) -> List[dict]:
        """Parse a JSON-format conversation export."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            log.error("Invalid JSON in conversation file.")
            return []

        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = (
                data.get("messages")
                or data.get("conversation")
                or data.get("entries")
                or []
            )
        else:
            return []

        messages: List[dict] = []
        for entry in entries:
            if isinstance(entry, dict):
                role = entry.get("role", entry.get("author", "unknown"))
                content = entry.get("content", entry.get("text", entry.get("message", "")))
                if isinstance(content, list):
                    content = "\n".join(
                        p.get("text", str(p)) if isinstance(p, dict) else str(p)
                        for p in content
                    )
                messages.append({"role": str(role), "content": str(content)})
        return messages

    # ------------------------------------------------------------------
    # Search & summary
    # ------------------------------------------------------------------

    def search(self, query: str) -> List[dict]:
        """Search all cached content for *query*."""
        query_lower = query.lower()
        matches: List[dict] = []

        for url, entry in self.cache.items():
            data = entry.get("data", {})
            if "messages" in data:
                for msg in data["messages"]:
                    content = msg.get("content", "")
                    if query_lower in content.lower():
                        idx = content.lower().index(query_lower)
                        snippet = f"...{content[max(0,idx-100):idx+200]}..."
                        matches.append({
                            "source": data.get("source", url),
                            "type": "conversation",
                            "role": msg.get("role", "unknown"),
                            "snippet": snippet,
                        })
            else:
                text = data.get("text", "")
                if query_lower in text.lower():
                    idx = text.lower().index(query_lower)
                    snippet = f"...{text[max(0,idx-100):idx+200]}..."
                    matches.append({
                        "source": data.get("url", url),
                        "type": "page",
                        "title": data.get("title", ""),
                        "snippet": snippet,
                    })
        return matches

    def get_summary(self) -> dict:
        """Return a quick summary of all cached content."""
        pages: List[dict] = []
        convos: List[dict] = []
        for entry in self.cache.values():
            data = entry.get("data", {})
            if "messages" in data:
                convos.append({
                    "source": data.get("source", "unknown"),
                    "message_count": data.get("message_count", 0),
                    "parsed_at": data.get("parsed_at", ""),
                })
            else:
                pages.append({
                    "url": data.get("url", ""),
                    "title": data.get("title", ""),
                    "headings": data.get("headings", [])[:5],
                })
        return {
            "site": self.base_url,
            "pages_cached": len(pages),
            "conversations_cached": len(convos),
            "pages": pages,
            "conversations": convos,
        }

    def clear_cache(self) -> None:
        self.cache = {}
        self._save_cache()
        log.info("Cache cleared.")


# Module-level singleton
scraper = OdinScraper()


if __name__ == "__main__":
    pages = scraper.scrape_all()
    for page in pages:
        print(f"\n--- {page['title']} ---")
        print(f"URL: {page['url']}")
        print(f"Text: {page['text'][:200]}…")
    print(json.dumps(scraper.get_summary(), indent=2))
