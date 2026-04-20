"""
Central configuration for Enki-AI / JARVIS.

Every hard-coded path or tunable constant lives here.  Override any value by
setting the corresponding environment variable before starting the assistant.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------
HOME = Path.home()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Piper TTS
# ---------------------------------------------------------------------------
PIPER_DIR: Path = Path(
    os.environ.get(
        "PIPER_DIR",
        str(HOME / "Downloads" / "piper_windows_amd64" / "piper"),
    )
)
PIPER_EXE: Path = PIPER_DIR / "piper.exe"
PIPER_VOICE: str = os.environ.get("PIPER_VOICE", "en_GB-vctk-medium")
PIPER_MODEL: Path = PIPER_DIR / "voices" / f"{PIPER_VOICE}.onnx"

# ---------------------------------------------------------------------------
# Wake word
# ---------------------------------------------------------------------------
WAKE_WORD: str = os.environ.get("WAKE_WORD", "jarvis").lower()

# ---------------------------------------------------------------------------
# Programs that JARVIS can open directly
# ---------------------------------------------------------------------------
PROGRAM_PATHS: dict[str, str] = {
    "wow": str(
        Path(
            os.environ.get(
                "JARVIS_WOW_PATH",
                r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe",
            )
        )
    ),
    "chrome": str(
        Path(
            os.environ.get(
                "JARVIS_CHROME_PATH",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            )
        )
    ),
    "discord": str(
        Path(
            os.environ.get(
                "JARVIS_DISCORD_PATH",
                str(
                    HOME
                    / "AppData"
                    / "Roaming"
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / "Discord Inc"
                    / "Discord.lnk"
                ),
            )
        )
    ),
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
SEARCH_DIRECTORIES: list[str] = [
    str(HOME / "Desktop"),
    str(HOME / "Downloads"),
    str(HOME / "Documents"),
]

INDEX_EXTENSIONS: tuple[str, ...] = (".exe", ".lnk", ".bat", ".docx", ".pdf")

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
