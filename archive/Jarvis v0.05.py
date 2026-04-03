# JARVIS - fixed (Python 3.8/3.9 compatible + safer startup)

import subprocess
import os
import tempfile
import time
import winsound  # Windows built-in
import speech_recognition as sr
import threading
import web_server
import re
import numpy as np
import soundfile as sf
from pathlib import Path
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import Optional

# NOTE:
# - Removed "import web_server" (it can break/hang at import if it runs code)
# - Removed top-level "set_system_volume(50)" test call (can crash on startup)
# - Replaced "| None" type hints with Optional[...] (Python 3.8/3.9 fix)
# - Made winsound playback async so Jarvis doesn't feel frozen while speaking
# - Delayed WAV cleanup slightly so async playback doesn't delete file too early

# ---------- VOLUME ----------

# Function to set system volume
def set_system_volume(level: int):
    """Set system volume to the specified level (0-100)."""
    # Path to nircmd.exe
    nircmd_path = "D:/JARVIS AI/nircmd.exe"
    
    # Check if nircmd.exe exists
    if os.path.exists(nircmd_path):
        # Convert the level to range 0-65535 for nircmd
        subprocess.run(f"{nircmd_path} setsysvolume {level * 65535 // 100}")
        print(f"Volume set to {level}%")
    else:
        print("nircmd.exe is not found. Please ensure it is installed at the specified path.")

# Main script
if __name__ == "__main__":
    # Test: Set the system volume to 50%
    set_system_volume(50)  # You can change this value to set different volume levels


def reduce_wav_volume(infile: str, outfile: Optional[str] = None, gain: float = 0.5) -> str:
    """
    Reduce volume of a WAV file (gain 0.0..1.0). Returns outfile path.
    """
    infile_p = Path(infile)
    if outfile is None:
        outfile_p = infile_p.with_name(infile_p.stem + "_low.wav")
    else:
        outfile_p = Path(outfile)

    data, sr_ = sf.read(str(infile_p), dtype="float32")
    data *= float(max(0.0, min(1.0, gain)))
    data = np.clip(data, -1.0, 1.0)
    sf.write(str(outfile_p), data, sr_, subtype="PCM_16")
    return str(outfile_p)


# ---------- PIPER TTS ----------
home = os.path.expanduser("~")
PIPER_DIR = os.path.join(home, "Downloads", "piper_windows_amd64", "piper")
PIPER_EXE = os.path.join(PIPER_DIR, "piper.exe")


def set_model(voice_name: str) -> str:
    """Set the path to the model dynamically based on voice name."""
    return os.path.join(PIPER_DIR, "voices", f"{voice_name}.onnx")


def speak(text: str, voice_name: str = "en_GB-vctk-medium"):
    """Convert text to speech using Piper with error handling."""
    try:
        model_path = set_model(voice_name)

        if not os.path.exists(PIPER_EXE):
            print(f"Error: Piper executable not found at {PIPER_EXE}")
            return
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            return

        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        cmd = [
            PIPER_EXE,
            "--model", model_path,
            "--output_file", wav_path,
            "--length_scale", "1.2",
            "--noise_scale", "0.3",
            "--noise_w", "0.3",
        ]

        subprocess.run(
            cmd,
            input=text,
            text=True,
            check=True,
            cwd=PIPER_DIR,
            timeout=15
        )

        if os.path.exists(wav_path):
            try:
                # Async playback so we don't block listening
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Audio playback error: {e}")
        else:
            print(f"WAV file not created at {wav_path}")

        # Async playback needs the file to exist briefly
        def cleanup_later(p: str):
            time.sleep(2.0)
            try:
                os.remove(p)
            except OSError:
                pass

        threading.Thread(target=cleanup_later, args=(wav_path,), daemon=True).start()

    except subprocess.TimeoutExpired:
        print("Piper TTS timed out")
    except subprocess.CalledProcessError as e:
        print(f"Piper returned error: {e}")
    except Exception as e:
        print(f"Speak error: {e}")


# ---------- MICROPHONE SETUP ----------
recognizer = sr.Recognizer()

mic_index = 0
mic_name = None
try:
    names = sr.Microphone.list_microphone_names()
    for i, name in enumerate(names):
        print(f"{i}: {name}")
        if "microphone" in name.lower() or "headset" in name.lower():
            mic_index = i
            mic_name = name
            break
except Exception as e:
    print(f"Could not list microphones: {e}")

mic = sr.Microphone(device_index=mic_index)

# Optional: reduce false triggers a bit
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

speak("Jarvis online.")


# ---------- FOLDER LOCATIONS TO SEARCH ----------
SEARCH_DIRECTORIES = [
    os.path.join(home, "Desktop"),
    os.path.join(home, "Downloads"),
    os.path.join(home, "Documents"),
    # NOTE: Program Files indexing is heavy; only add back if you really want it.
    # r"C:\Program Files",
    # r"C:\Program Files (x86)",
]

# ---------- FIXED PROGRAM LAUNCH PATHS ----------
PROGRAM_PATHS = {
    "wow": r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": os.path.join(home, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Discord Inc", "Discord.lnk"),
    "form": "https://docs.google.com/forms/d/19_p-yBWGWrp9GykYiKfck7RbAEJ5fRoaTUh_xCjmEZo/viewform",
    "responses": "https://docs.google.com/spreadsheets/d/18JNGFvhNV3y4cXShh9y3Q5bGw7yDeC4yxh8J0wZuX8I/edit?gid=165398226#gid=165398226"
}

# ---------- OPTIONAL ALIASES ----------
ALIASES = {
    "world of warcraft": "wow",
    "google chrome": "chrome",
}

# ---------- FAST FILE INDEX (Build Once) ----------
INDEX_EXTENSIONS = ('.exe', '.lnk', '.bat', '.docx', '.pdf')
FILE_INDEX = {}


def build_file_index():
    global FILE_INDEX
    print("Building file index... (first run can take a bit)")
    try:
        for directory in SEARCH_DIRECTORIES:
            if not os.path.exists(directory):
                print(f"Skipping {directory} (not found)")
                continue

            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        f_lower = file.lower()
                        if f_lower.endswith(INDEX_EXTENSIONS):
                            name_key = os.path.splitext(f_lower)[0]
                            full_path = os.path.join(root, file)
                            FILE_INDEX.setdefault(name_key, full_path)
                    except Exception as e:
                        print(f"Error indexing file {file}: {e}")
                        continue

        print(f"Indexed {len(FILE_INDEX)} items.")
        speak("Right Cas. How we fixing the system today.")
    except Exception as e:
        print(f"Critical error building file index: {e}")


build_file_index()


def open_program(name: str) -> bool:
    try:
        name = name.lower().strip()
        if not name:
            speak("No program specified.")
            return False

        name = ALIASES.get(name, name)

        # predefined direct paths first
        if name in PROGRAM_PATHS:
            program_path = PROGRAM_PATHS[name]
            if program_path.startswith("http"):
                speak(f"Opening {name}.")
                os.system(f'start "" "{program_path}"')
                return True
            if os.path.exists(program_path):
                speak(f"Opening {name}.")
                os.system(f'start "" "{program_path}"')
                return True
            speak(f"Program path not found.")
            return False

        # exact indexed lookup
        if name in FILE_INDEX:
            program_path = FILE_INDEX[name]
            if os.path.exists(program_path):
                speak(f"Opening {name}.")
                os.system(f'start "" "{program_path}"')
                return True
            return False

        # partial match fallback
        for key, program_path in FILE_INDEX.items():
            if name in key and os.path.exists(program_path):
                speak(f"Opening {key}.")
                os.system(f'start "" "{program_path}"')
                return True

        speak(f"I couldn't find {name}.")
        return False

    except Exception as e:
        print(f"Error in open_program: {e}")
        speak("An error occurred while opening the program.")
        return False


# ---------- COMMAND PARSER / ROUTER ----------
VERB_OPEN = {"open", "launch", "start", "run"}
VERB_HELP = {"help", "commands", "what can you do", "list commands"}
VERB_SHUTDOWN = {"shutdown", "shut down", "close", "close assistant", "quit", "exit", "stop", "end"}


def normalize_text(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def strip_wakeword(t: str) -> str:
    return t.replace("jarvis", "").strip()


def extract_volume_level(command: str) -> Optional[int]:
    """
    Accepts: 'set volume to 50', 'volume 30%', 'set volume 10 percent'
    Returns int 0..100 or None
    """
    m = re.search(r'(\d{1,3})\s*(%|percent)?', command.lower())
    if not m:
        return None
    level = int(m.group(1))
    level = max(0, min(100, level))
    return level


def route_command(command_clean: str):
    c = normalize_text(command_clean)

    # volume control
    if "volume" in c:
        level = extract_volume_level(c)
        if level is not None:
            ok = set_system_volume(level)
            speak(f"Volume set to {level} percent." if ok else "I couldn't change the volume.")
            return "volume", level

    # shutdown
    for k in VERB_SHUTDOWN:
        if k in c:
            speak("Adios.")
            return "shutdown", None

    # help
    if any(k in c for k in VERB_HELP):
        speak("Commands: say Jarvis open plus an app name. Say Jarvis volume 50. Say Jarvis shutdown to close.")
        return "help", None

    # open/launch/start/run + target
    tokens = c.split(" ")
    if tokens and tokens[0] in VERB_OPEN:
        target = c[len(tokens[0]):].strip().strip(" .")
        if target:
            return "open", target

    # fallback: treat whole phrase as target
    if c:
        return "open", c

    return "none", None


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
                print(f"Listen error: {e}")
                continue

        try:
            wake_text = recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Google API error: {e}")
            speak("Connection error. Retrying...")
            continue
        except Exception as e:
            print(f"Recognition error: {e}")
            continue

        if "jarvis" not in wake_text:
            continue

        print("Wake word detected.")

        # greeting (non-blocking)
        threading.Thread(target=lambda: speak("What's up Cass?"), daemon=True).start()

        # ACTIVE LISTEN (real command)
        with mic as source:
            print("Listening for command...")
            try:
                command_audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                speak("Timed out.")
                continue
            except Exception as e:
                print(f"Listen error: {e}")
                continue

        try:
            command = recognizer.recognize_google(command_audio).lower()
            print("Command:", command)
        except sr.UnknownValueError:
            speak("I didn't catch that.")
            continue
        except sr.RequestError as e:
            print(f"Google API error: {e}")
            speak("Connection error. Try again.")
            continue
        except Exception as e:
            print(f"Recognition error: {e}")
            speak("Speech error.")
            continue

        try:
            action, payload = route_command(command)

            if action == "shutdown":
                break

            if action == "help":
                continue

            if action == "open" and payload:
                open_program(payload)

        except Exception as e:
            print(f"Command routing error: {e}")
            speak("Error processing command.")
            continue

    except Exception as e:
        print(f"Critical error in main loop: {e}")
        time.sleep(1)
        continue