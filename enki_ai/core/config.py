"""
Central configuration for Enki-AI / JARVIS.

Every hard-coded path or tunable constant lives here.  Override any value by
setting the corresponding environment variable before starting the assistant.

Linux quick-start
-----------------
Set the following environment variables (or copy .env.template to .env):

    PIPER_DIR   – path to your Piper TTS installation (see linux/install.sh)
    PIPER_VOICE – voice model name (default: en_GB-vctk-medium)
    GEMINI_API_KEY – your Google Gemini API key
"""

import os
import platform
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------
HOME = Path.home()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
_IS_WINDOWS: bool = sys.platform == "win32"
_IS_LINUX: bool = sys.platform.startswith("linux")
_IS_MACOS: bool = sys.platform == "darwin"

# ---------------------------------------------------------------------------
# Piper TTS
# ---------------------------------------------------------------------------
# Default Piper installation directory is platform-aware.
# Windows: ~/Downloads/piper_windows_amd64/piper
# Linux:   ~/piper   (see linux/install.sh for setup)
# macOS:   ~/piper
_PIPER_DEFAULT_DIR: str = (
    str(HOME / "Downloads" / "piper_windows_amd64" / "piper")
    if _IS_WINDOWS
    else str(HOME / "piper")
)

PIPER_DIR: Path = Path(os.environ.get("PIPER_DIR", _PIPER_DEFAULT_DIR))

# The executable name differs by platform:  'piper.exe' on Windows, 'piper' elsewhere.
_PIPER_EXE_NAME: str = "piper.exe" if _IS_WINDOWS else "piper"
PIPER_EXE: Path = PIPER_DIR / _PIPER_EXE_NAME

PIPER_VOICE: str = os.environ.get("PIPER_VOICE", "en_GB-vctk-medium")
PIPER_MODEL: Path = PIPER_DIR / "voices" / f"{PIPER_VOICE}.onnx"

# ---------------------------------------------------------------------------
# Wake word
# ---------------------------------------------------------------------------
WAKE_WORD: str = os.environ.get("WAKE_WORD", "jarvis").lower()

# ---------------------------------------------------------------------------
# Programs that JARVIS can open directly
# ---------------------------------------------------------------------------
# Defaults are platform-aware.  Override any entry with the corresponding
# environment variable (e.g. JARVIS_CHROME_PATH).
def _chrome_default() -> str:
    if _IS_WINDOWS:
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if _IS_MACOS:
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    # Linux: prefer system path; fall back to common Snap/Flatpak locations
    for p in (
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium",
    ):
        if os.path.exists(p):
            return p
    return "/usr/bin/google-chrome"


def _discord_default() -> str:
    if _IS_WINDOWS:
        return str(
            HOME
            / "AppData"
            / "Roaming"
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Discord Inc"
            / "Discord.lnk"
        )
    if _IS_MACOS:
        return "/Applications/Discord.app/Contents/MacOS/Discord"
    # Linux
    for p in (
        str(HOME / ".local" / "bin" / "discord"),
        "/usr/bin/discord",
        "/snap/bin/discord",
        str(HOME / "snap" / "discord" / "current" / "discord"),
    ):
        if os.path.exists(p):
            return p
    return "/usr/bin/discord"


def _wow_default() -> str:
    if _IS_WINDOWS:
        return r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe"
    if _IS_MACOS:
        return "/Applications/World of Warcraft/_retail_/World of Warcraft.app/Contents/MacOS/World of Warcraft"
    # Linux (common Lutris/Wine path)
    return str(HOME / "Games" / "world-of-warcraft" / "drive_c" / "Program Files (x86)" / "World of Warcraft" / "_retail_" / "Wow.exe")


PROGRAM_PATHS: dict[str, str] = {
    "wow": os.environ.get("JARVIS_WOW_PATH", _wow_default()),
    "chrome": os.environ.get("JARVIS_CHROME_PATH", _chrome_default()),
    "discord": os.environ.get("JARVIS_DISCORD_PATH", _discord_default()),
    "form": os.environ.get(
        "JARVIS_FORM_URL",
        "https://docs.google.com/forms/d/19_p-yBWGWrp9GykYiKfck7RbAEJ5fRoaTUh_xCjmEZo/viewform",
    ),
    "responses": os.environ.get(
        "JARVIS_RESPONSES_URL",
        "https://docs.google.com/spreadsheets/d/18JNGFvhNV3y4cXShh9y3Q5bGw7yDeC4yxh8J0wZuX8I/edit?gid=165398226#gid=165398226",
    ),
}

ALIASES: dict[str, str] = {
    "world of warcraft": "wow",
    "google chrome": "chrome",
}

# ---------------------------------------------------------------------------
# File-index search directories
# ---------------------------------------------------------------------------
_BASE_SEARCH_DIRS: list[str] = [
    str(HOME / "Desktop"),
    str(HOME / "Downloads"),
    str(HOME / "Documents"),
]
# On Linux, also search ~/.local/bin (user-installed apps) and /usr/bin
if _IS_LINUX:
    _BASE_SEARCH_DIRS += [
        str(HOME / ".local" / "bin"),
        "/usr/bin",
        "/usr/local/bin",
    ]

SEARCH_DIRECTORIES: list[str] = [
    d for d in os.environ.get("JARVIS_SEARCH_DIRS", "").split(":")
    if d
] or _BASE_SEARCH_DIRS

INDEX_EXTENSIONS: tuple[str, ...] = (
    # Windows
    ".exe", ".lnk", ".bat",
    # Cross-platform / Linux
    ".sh", ".desktop",
    # Documents (all platforms)
    ".docx", ".pdf",
)

# ---------------------------------------------------------------------------
# API / Database
# ---------------------------------------------------------------------------
API_HOST: str = os.environ.get("API_HOST", "127.0.0.1")
API_PORT: int = int(os.environ.get("API_PORT", "5000"))
DB_PATH: str = os.environ.get(
    "DB_PATH", str(PROJECT_ROOT / "data" / "form_submissions.db")
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

# ---------------------------------------------------------------------------
# Gemini LLM (SovereignBrain)
# ---------------------------------------------------------------------------
# The google-genai SDK also reads GEMINI_API_KEY automatically; setting it
# here gives the rest of the codebase a single, consistent config source.
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
