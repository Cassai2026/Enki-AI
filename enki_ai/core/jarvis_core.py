"""
JARVIS core – voice assistant engine.

This is the canonical entry point for the JARVIS assistant.  It replaces the
scattered versioned scripts (V0.01 – V0.06).

Run directly:
    python -m enki_ai.core.jarvis_core

Environment overrides (see config.py for full list):
    PIPER_DIR, PIPER_VOICE, WAKE_WORD, LOG_LEVEL
"""

import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from typing import Optional, Tuple

from enki_ai.core import config

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("jarvis")

# ---------------------------------------------------------------------------
# Cross-platform WAV playback
# ---------------------------------------------------------------------------


def _play_wav_async(wav_path: str) -> None:
    """Play a WAV file asynchronously.  Falls back gracefully on non-Windows."""
    try:
        import winsound  # type: ignore[import]

        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        return
    except ImportError:
        pass

    # Linux: aplay
    try:
        subprocess.Popen(
            ["aplay", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except FileNotFoundError:
        pass

    # macOS: afplay
    try:
        subprocess.Popen(
            ["afplay", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except FileNotFoundError:
        pass

    log.warning("No audio playback tool found (winsound / aplay / afplay missing).")


# ---------------------------------------------------------------------------
# Piper TTS
# ---------------------------------------------------------------------------


def speak(text: str) -> None:
    """Convert *text* to speech via Piper TTS and play the result."""
    try:
        piper_exe = str(config.PIPER_EXE)
        model = str(config.PIPER_MODEL)

        if not os.path.exists(piper_exe):
            log.warning("Piper executable not found at %s – printing instead.", piper_exe)
            print(f"[JARVIS] {text}")
            return
        if not os.path.exists(model):
            log.warning("Piper model not found at %s – printing instead.", model)
            print(f"[JARVIS] {text}")
            return

        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        cmd = [
            piper_exe,
            "--model", model,
            "--output_file", wav_path,
            "--text", text,
        ]
        result = subprocess.run(cmd, timeout=15, capture_output=True)
        if result.returncode != 0:
            log.error("Piper error: %s", result.stderr.decode(errors="replace"))
            return

        _play_wav_async(wav_path)

        def _cleanup(p: str) -> None:
            time.sleep(3.0)
            try:
                os.remove(p)
            except OSError:
                pass

        threading.Thread(target=_cleanup, args=(wav_path,), daemon=True).start()

    except subprocess.TimeoutExpired:
        log.error("Piper TTS timed out.")
    except Exception as exc:
        log.error("speak() error: %s", exc)


# ---------------------------------------------------------------------------
# Volume control (Windows via pycaw; graceful no-op elsewhere)
# ---------------------------------------------------------------------------


def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(n)))


def get_system_volume() -> Optional[int]:
    """Return master volume 0–100, or *None* if unavailable."""
    try:
        from ctypes import POINTER, cast  # type: ignore[import]
        from comtypes import CLSCTX_ALL  # type: ignore[import]
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore[import]

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return int(round(float(volume.GetMasterVolumeLevelScalar()) * 100))
    except Exception as exc:
        log.debug("get_system_volume: %s", exc)
        return None


def set_system_volume(level: int) -> bool:
    """Set master volume to *level* (0–100).  Returns *True* on success."""
    try:
        from ctypes import POINTER, cast  # type: ignore[import]
        from comtypes import CLSCTX_ALL  # type: ignore[import]
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore[import]

        level = _clamp(level)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        log.info("Volume set to %d%%", level)
        return True
    except Exception as exc:
        log.debug("set_system_volume: %s", exc)
        return False


def mute_system(mute: bool = True) -> bool:
    """Mute or unmute master output.  Returns *True* on success."""
    try:
        from ctypes import POINTER, cast  # type: ignore[import]
        from comtypes import CLSCTX_ALL  # type: ignore[import]
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore[import]

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1 if mute else 0, None)
        log.info("Mute=%s", mute)
        return True
    except Exception as exc:
        log.debug("mute_system: %s", exc)
        return False


def change_volume(delta: int) -> Tuple[bool, Optional[int]]:
    """Adjust current volume by *delta*.  Returns ``(ok, new_level)``."""
    cur = get_system_volume()
    if cur is None:
        return False, None
    new_level = _clamp(cur + int(delta))
    ok = set_system_volume(new_level)
    return ok, (new_level if ok else None)


def extract_volume_number(text: str) -> Optional[int]:
    """Pull the first number 0–100 out of *text*."""
    m = re.search(r"(\d{1,3})\s*(%|percent)?", text.lower())
    if not m:
        return None
    return _clamp(int(m.group(1)))


# ---------------------------------------------------------------------------
# Program launcher
# ---------------------------------------------------------------------------

# File-index built once at startup
FILE_INDEX: dict[str, str] = {}


def build_file_index() -> None:
    """Walk SEARCH_DIRECTORIES and cache paths of launchable files."""
    global FILE_INDEX
    log.info("Building file index (first run may take a moment)…")
    try:
        for directory in config.SEARCH_DIRECTORIES:
            if not os.path.exists(directory):
                log.debug("Skipping %s (not found)", directory)
                continue
            for root, _dirs, files in os.walk(directory):
                for file in files:
                    try:
                        f_lower = file.lower()
                        if f_lower.endswith(config.INDEX_EXTENSIONS):
                            name_key = os.path.splitext(f_lower)[0]
                            full_path = os.path.join(root, file)
                            FILE_INDEX.setdefault(name_key, full_path)
                    except Exception as exc:
                        log.debug("Index error for %s: %s", file, exc)
        log.info("File index ready: %d items.", len(FILE_INDEX))
    except Exception as exc:
        log.error("build_file_index failed: %s", exc)


def open_program(name: str) -> bool:
    """Open a named program or URL.  Returns *True* on success."""
    name = (name or "").lower().strip()
    if not name:
        speak("No program specified.")
        return False

    name = config.ALIASES.get(name, name)

    if name in config.PROGRAM_PATHS:
        target = config.PROGRAM_PATHS[name]
        speak(f"Opening {name}.")
        try:
            os.startfile(target) if hasattr(os, "startfile") else subprocess.Popen(["xdg-open", target])  # type: ignore[attr-defined]
            return True
        except Exception as exc:
            log.error("open_program %s: %s", name, exc)
            speak("I couldn't open that.")
            return False

    # Exact index lookup
    if name in FILE_INDEX and os.path.exists(FILE_INDEX[name]):
        speak(f"Opening {name}.")
        try:
            os.startfile(FILE_INDEX[name]) if hasattr(os, "startfile") else subprocess.Popen(["xdg-open", FILE_INDEX[name]])  # type: ignore[attr-defined]
            return True
        except Exception as exc:
            log.error("open_program (index) %s: %s", name, exc)
            speak("I couldn't open that.")
            return False

    # Partial match fallback
    for key, path in FILE_INDEX.items():
        if name in key and os.path.exists(path):
            speak(f"Opening {key}.")
            try:
                os.startfile(path) if hasattr(os, "startfile") else subprocess.Popen(["xdg-open", path])  # type: ignore[attr-defined]
                return True
            except Exception as exc:
                log.error("open_program (partial) %s: %s", key, exc)

    speak("I don't have that mapped yet.")
    return False


# ---------------------------------------------------------------------------
# Command routing
# ---------------------------------------------------------------------------

_VERB_OPEN = {"open", "launch", "start", "run"}
_VERB_HELP = {"help", "commands", "list commands", "what can you do"}
_VERB_SHUTDOWN = {
    "shutdown",
    "shut down",
    "quit",
    "exit",
    "close assistant",
    "stop",
    "end",
}


def normalize_text(t: str) -> str:
    t = (t or "").lower().strip()
    return re.sub(r"\s+", " ", t)


def route_command(command: str) -> Tuple[str, Optional[str]]:
    """
    Parse *command* and return ``(action, payload)``.

    Actions: ``volume_set``, ``volume_up``, ``volume_down``, ``mute``,
    ``unmute``, ``open``, ``help``, ``shutdown``, ``none``.
    """
    c = normalize_text(command)

    if any(k in c for k in _VERB_SHUTDOWN):
        return "shutdown", None
    if any(k in c for k in _VERB_HELP):
        return "help", None
    if "unmute" in c:
        return "unmute", None
    if "mute" in c:
        return "mute", None

    if "volume" in c or any(k in c for k in ("louder", "quieter", "increase", "decrease")):
        if "up" in c or "increase" in c or "louder" in c:
            n = extract_volume_number(c)
            return "volume_up", str(n if n is not None else 10)
        if "down" in c or "decrease" in c or "quieter" in c or "lower" in c:
            n = extract_volume_number(c)
            return "volume_down", str(n if n is not None else 10)
        n = extract_volume_number(c)
        return ("volume_set", str(n)) if n is not None else ("volume_set", None)

    tokens = c.split()
    if tokens and tokens[0] in _VERB_OPEN:
        target = c[len(tokens[0]):].strip()
        return ("open", target) if target else ("none", None)

    if c:
        return "open", c
    return "none", None


def do_help() -> None:
    speak(
        "Commands: say Jarvis volume 50, volume up 10, mute, "
        "open chrome, or shutdown."
    )


# ---------------------------------------------------------------------------
# Microphone / speech recognition
# ---------------------------------------------------------------------------


def _setup_mic():
    """Initialise SpeechRecognition and pick the best microphone."""
    try:
        import speech_recognition as sr  # type: ignore[import]
    except ImportError:
        log.error("speech_recognition not installed.  Run: pip install SpeechRecognition")
        return None, None

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    mic_index = 0
    try:
        names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(names):
            log.debug("Mic %d: %s", i, name)
            if "microphone" in name.lower() or "headset" in name.lower():
                mic_index = i
                break
    except Exception as exc:
        log.warning("Could not list microphones: %s", exc)

    return recognizer, sr.Microphone(device_index=mic_index)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run() -> None:
    """Start the JARVIS wake-word listen loop.  Blocks until shutdown."""
    try:
        import speech_recognition as sr  # type: ignore[import]
    except ImportError:
        log.error("speech_recognition not installed.  Run: pip install SpeechRecognition")
        sys.exit(1)

    build_file_index()
    recognizer, mic = _setup_mic()
    if mic is None:
        log.error("No microphone available.  Exiting.")
        sys.exit(1)

    speak("Jarvis online.")
    log.info("JARVIS ready – say '%s' to wake.", config.WAKE_WORD)

    while True:
        try:
            # Passive listen: detect wake word
            with mic as source:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    print(".", end="", flush=True)
                    continue
                except Exception as exc:
                    log.debug("listen error: %s", exc)
                    continue

            try:
                wake_text = recognizer.recognize_google(audio).lower()
            except sr.UnknownValueError:
                continue
            except sr.RequestError as exc:
                log.warning("Google API error: %s", exc)
                speak("Connection error.")
                continue
            except Exception as exc:
                log.debug("recognition error: %s", exc)
                continue

            if config.WAKE_WORD not in wake_text:
                continue

            log.info("Wake word detected.")
            threading.Thread(target=lambda: speak("What's up?"), daemon=True).start()

            # Active listen: get the actual command
            with mic as source:
                log.info("Listening for command…")
                try:
                    command_audio = recognizer.listen(
                        source, timeout=6, phrase_time_limit=7
                    )
                except sr.WaitTimeoutError:
                    speak("Timed out.")
                    continue
                except Exception as exc:
                    log.debug("listen2 error: %s", exc)
                    continue

            try:
                command = recognizer.recognize_google(command_audio).lower()
                log.info("Command: %s", command)
            except sr.UnknownValueError:
                speak("I didn't catch that.")
                continue
            except sr.RequestError as exc:
                log.warning("Google API error: %s", exc)
                speak("Connection error.")
                continue
            except Exception as exc:
                log.debug("recognition2 error: %s", exc)
                speak("Speech error.")
                continue

            action, payload = route_command(command)

            if action == "shutdown":
                speak("Adios.")
                break
            elif action == "help":
                do_help()
            elif action == "mute":
                speak("Muted." if mute_system(True) else "I couldn't mute.")
            elif action == "unmute":
                speak("Unmuted." if mute_system(False) else "I couldn't unmute.")
            elif action == "volume_set":
                if payload is None:
                    speak("Say a number from 0 to 100.")
                else:
                    ok = set_system_volume(int(payload))
                    speak(
                        f"Volume set to {payload} percent."
                        if ok
                        else "I couldn't change the volume."
                    )
            elif action == "volume_up":
                delta = int(payload) if payload else 10
                ok, new_level = change_volume(+delta)
                speak(
                    f"Volume {new_level} percent."
                    if ok and new_level is not None
                    else "I couldn't change the volume."
                )
            elif action == "volume_down":
                delta = int(payload) if payload else 10
                ok, new_level = change_volume(-delta)
                speak(
                    f"Volume {new_level} percent."
                    if ok and new_level is not None
                    else "I couldn't change the volume."
                )
            elif action == "open" and payload:
                open_program(payload)
            else:
                speak("I didn't understand that.  Say help for commands.")

        except Exception as exc:
            log.error("Critical loop error: %s", exc)
            time.sleep(1)


if __name__ == "__main__":
    run()
