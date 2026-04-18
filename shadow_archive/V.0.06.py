# =========================
# JARVIS v0.x (FULL FILE)
# Volume commands included and SAFE (won't crash your assistant)
# Python 3.8/3.9/3.10+ compatible
# =========================

import subprocess
import os
import tempfile
import time
import winsound
import speech_recognition as sr
import threading
import re
from typing import Optional, Tuple

# ---------- PIPER TTS ----------
HOME = os.path.expanduser("~")
PIPER_DIR = r"C:\Users\pcass\Downloads\piper_windows_amd64\piper"
PIPER_EXE = os.path.join(PIPER_DIR, "piper.exe")
MODEL = os.path.join(PIPER_DIR, "voices", "en_GB-vctk-medium.onnx")

def speak(text: str):
    try:
        cmd = [
            PIPER_EXE,
            "--model", MODEL,
            "--output_file", "output.wav",
            "--text", text
        ]
        subprocess.run(cmd)
        wav_path = "output.wav"

        # async playback
        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        # cleanup after a short delay (so async playback isn't deleting the file mid-play)
        def cleanup(p: str):
            time.sleep(2.0)
            try:
                os.remove(p)
            except OSError:
                pass

        threading.Thread(target=cleanup, args=(wav_path,), daemon=True).start()

    except Exception as e:
        print(f"[TTS ERROR] {e}")


# ---------- VOLUME (SAFE) ----------
def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(n)))


def get_system_volume() -> Optional[int]:
    """Returns 0..100 or None if unavailable."""
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        scalar = volume.GetMasterVolumeLevelScalar()  # 0.0..1.0
        return int(round(float(scalar) * 100))
    except Exception as e:
        print(f"[VOL GET ERROR] {e}")
        return None


def set_system_volume(level: int) -> bool:
    """Sets master volume 0..100. Never crashes the app."""
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        level = _clamp(level)

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        print(f"[VOL] set {level}%")
        return True
    except Exception as e:
        print(f"[VOL SET ERROR] {e}")
        return False


def mute_system(mute: bool = True) -> bool:
    """Mute/unmute master output. Never crashes."""
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1 if mute else 0, None)
        print(f"[VOL] mute={mute}")
        return True
    except Exception as e:
        print(f"[VOL MUTE ERROR] {e}")
        return False


def change_volume(delta: int) -> Tuple[bool, Optional[int]]:
    """Adjust current volume by delta. Returns (ok, new_level)."""
    cur = get_system_volume()
    if cur is None:
        return False, None
    new_level = _clamp(cur + int(delta))
    ok = set_system_volume(new_level)
    return ok, (new_level if ok else None)


def extract_volume_number(text: str) -> Optional[int]:
    """Pull first number 0..100 from text."""
    m = re.search(r'(\d{1,3})\s*(%|percent)?', text.lower())
    if not m:
        return None
    return _clamp(int(m.group(1)))


# ---------- PROGRAM OPEN ----------
PROGRAM_PATHS = {
    "wow": r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": os.path.join(HOME, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Discord Inc", "Discord.lnk"),
    "form": "https://docs.google.com/forms/d/19_p-yBWGWrp9GykYiKfck7RbAEJ5fRoaTUh_xCjmEZo/viewform",
    "responses": "https://docs.google.com/spreadsheets/d/18JNGFvhNV3y4cXShh9y3Q5bGw7yDeC4yxh8J0wZuX8I/edit?gid=165398226#gid=165398226",
}

ALIASES = {
    "world of warcraft": "wow",
    "google chrome": "chrome",
}


def open_program(name: str) -> bool:
    name = (name or "").lower().strip()
    if not name:
        speak("No program specified.")
        return False

    name = ALIASES.get(name, name)

    if name in PROGRAM_PATHS:
        target = PROGRAM_PATHS[name]
        speak(f"Opening {name}.")
        try:
            os.system(f'start "" "{target}"')
            return True
        except Exception as e:
            print(f"[OPEN ERROR] {e}")
            speak("I couldn't open that.")
            return False

    speak("I don't have that app mapped yet.")
    return False


# ---------- COMMAND ROUTER ----------
VERB_OPEN = {"open", "launch", "start", "run"}
VERB_HELP = {"help", "commands", "list commands", "what can you do"}
VERB_SHUTDOWN = {"shutdown", "shut down", "quit", "exit", "close assistant", "stop", "end"}


def normalize_text(t: str) -> str:
    t = (t or "").lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def route_command(command: str) -> Tuple[str, Optional[str]]:
    """
    Returns: (action, payload)
    Actions:
      - volume_set payload=number string
      - volume_up payload=delta string
      - volume_down payload=delta string
      - mute payload=None
      - unmute payload=None
      - open payload=target
      - help payload=None
      - shutdown payload=None
      - none payload=None
    """
    c = normalize_text(command)

    # shutdown
    if any(k in c for k in VERB_SHUTDOWN):
        return "shutdown", None

    # help
    if any(k in c for k in VERB_HELP):
        return "help", None

    # mute/unmute
    if "mute" in c and "unmute" not in c:
        return "mute", None
    if "unmute" in c:
        return "unmute", None

    # volume commands
    # "volume 50" / "set volume to 50" / "volume 50 percent"
    if "volume" in c:
        # "volume up" / "turn it up" / "volume up 10"
        if "up" in c or "increase" in c or "louder" in c:
            n = extract_volume_number(c)
            delta = n if n is not None else 10
            return "volume_up", str(delta)

        # "volume down" / "turn it down" / "quieter" / "volume down 10"
        if "down" in c or "decrease" in c or "quieter" in c or "lower" in c:
            n = extract_volume_number(c)
            delta = n if n is not None else 10
            return "volume_down", str(delta)

        # set absolute
        n = extract_volume_number(c)
        if n is not None:
            return "volume_set", str(n)
        return "volume_set", None  # asked for volume but gave no number

    # open: "open chrome" etc
    tokens = c.split(" ")
    if tokens and tokens[0] in VERB_OPEN:
        target = c[len(tokens[0]):].strip().strip(" .")
        return ("open", target) if target else ("none", None)

    # fallback: treat as open target
    if c:
        return "open", c

    return "none", None


def do_help():
    speak(
        "Commands. Say Jarvis volume 50. Say Jarvis volume up 10. Say Jarvis mute. "
        "Say Jarvis open chrome. Say Jarvis shutdown."
    )


# ---------- MICROPHONE ----------
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

mic_index = 0
try:
    names = sr.Microphone.list_microphone_names()
    for i, name in enumerate(names):
        print(f"{i}: {name}")
        if "microphone" in name.lower() or "headset" in name.lower():
            mic_index = i
            break
except Exception as e:
    print(f"[MIC LIST ERROR] {e}")

mic = sr.Microphone(device_index=mic_index)

# boot message
speak("Jarvis online.")
print("JARVIS ready. Say 'Jarvis' to wake.")


# ---------- MAIN LOOP ----------
while True:
    try:
        # PASSIVE LISTEN (wake check)
        with mic as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                print(".", end="", flush=True)
                continue
            except Exception as e:
                print(f"[LISTEN ERROR] {e}")
                continue

        try:
            wake_text = recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[GOOGLE ERROR] {e}")
            speak("Connection error.")
            continue
        except Exception as e:
            print(f"[RECOG ERROR] {e}")
            continue

        if "jarvis" not in wake_text:
            continue

        print("\nWake word detected.")

        # Quick greeting (non-blocking)
        threading.Thread(target=lambda: speak("What's up Cass?"), daemon=True).start()

        # ACTIVE LISTEN (command)
        with mic as source:
            print("Listening for command...")
            try:
                command_audio = recognizer.listen(source, timeout=6, phrase_time_limit=7)
            except sr.WaitTimeoutError:
                speak("Timed out.")
                continue
            except Exception as e:
                print(f"[LISTEN2 ERROR] {e}")
                continue

        try:
            command = recognizer.recognize_google(command_audio).lower()
            print("Command:", command)
        except sr.UnknownValueError:
            speak("I didn't catch that.")
            continue
        except sr.RequestError as e:
            print(f"[GOOGLE ERROR] {e}")
            speak("Connection error.")
            continue
        except Exception as e:
            print(f"[RECOG2 ERROR] {e}")
            speak("Speech error.")
            continue

        action, payload = route_command(command)

        # ---------- ACTIONS ----------
        if action == "shutdown":
            speak("Adios.")
            break

        if action == "help":
            do_help()
            continue

        if action == "mute":
            ok = mute_system(True)
            speak("Muted." if ok else "I couldn't mute.")
            continue

        if action == "unmute":
            ok = mute_system(False)
            speak("Unmuted." if ok else "I couldn't unmute.")
            continue

        if action == "volume_set":
            if payload is None:
                speak("Say a number from 0 to 100.")
                continue
            ok = set_system_volume(int(payload))
            speak(f"Volume set to {payload} percent." if ok else "I couldn't change the volume.")
            continue

        if action == "volume_up":
            delta = int(payload) if payload else 10
            ok, new_level = change_volume(+delta)
            speak(f"Volume {new_level} percent." if ok and new_level is not None else "I couldn't change the volume.")
            continue

        if action == "volume_down":
            delta = int(payload) if payload else 10
            ok, new_level = change_volume(-delta)
            speak(f"Volume {new_level} percent." if ok and new_level is not None else "I couldn't change the volume.")
            continue

        if action == "open" and payload:
            open_program(payload)
            continue

        # fallback
        speak("I didn't understand that. Say help for commands.")

    except Exception as e:
        print(f"[CRITICAL LOOP ERROR] {e}")
        time.sleep(1)
        continue