import subprocess
import os
import tempfile
import time
import winsound  # Windows built-in
import speech_recognition as sr
import threading
import re
import web_server
import numpy as np
import soundfile as sf
from pathlib import Path

def reduce_wav_volume(infile: str, outfile: str | None = None, gain: float = 0.5) -> str:
    """
    Reduce volume of a WAV file (gain 0.0..1.0). Returns outfile path.
    """
    infile = Path(infile)
    if outfile is None:
        outfile = infile.with_name(infile.stem + "_low.wav")
    data, sr = sf.read(str(infile), dtype="float32")
    data *= float(max(0.0, min(1.0, gain)))
    data = np.clip(data, -1.0, 1.0)
    sf.write(str(outfile), data, sr, subtype="PCM_16")
    return str(outfile)

# Call this right after Piper writes the WAV and before playback:
# piper_wav = "path/to/piper_output.wav"
# low_wav = reduce_wav_volume(piper_wav, gain=0.5)
# play low_wav instead of piper_wav

# Path to Piper directory and executable
home = os.path.expanduser("~")
PIPER_DIR = os.path.join(home, "Downloads", "piper_windows_amd64", "piper")
PIPER_EXE = os.path.join(PIPER_DIR, "piper.exe")

def set_model(voice_name: str):
    """Set the path to the model dynamically based on voice name"""
    model_path = os.path.join(PIPER_DIR, "voices", f"{voice_name}.onnx")
    return model_path

def speak(text: str, voice_name: str = "en_GB-vctk-medium"):
    """Convert text to speech using Piper with error handling"""
    try:
        # Set the model dynamically
        MODEL = set_model(voice_name)

        if not os.path.exists(MODEL):
            print(f"Error: Model file not found at {MODEL}")
            return

        # Create a temp wav path
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        # Run Piper: send text via stdin, write wav to file
        cmd = [
            PIPER_EXE,
            "--model", MODEL,
            "--output_file", wav_path,
            "--length_scale", "1.2",
            "--noise_scale", "0.3",
            "--noise_w", "0.3",
        ]

        subprocess.run(cmd, input=text, text=True, check=True, cwd=PIPER_DIR, timeout=10)

        # Play the wav (blocking)
        if os.path.exists(wav_path):
            try:
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            except Exception as e:
                print(f"Audio playback error: {e}")
        else:
            print(f"WAV file not created at {wav_path}")

        # Clean up file
        try:
            os.remove(wav_path)
        except OSError:
            pass
    except subprocess.TimeoutExpired:
        print("Piper TTS timed out")
    except FileNotFoundError:
        print(f"Error: Piper executable not found at {PIPER_EXE}")
    except Exception as e:
        print(f"Speak error: {e}")

# ---------- MICROPHONE SETUP ----------
recognizer = sr.Recognizer()

# Automatically pick the first available microphone
mic_index = 0
mic_name = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")
    if "microphone" in name.lower() or "headset" in name.lower():
        mic_index = i
        mic_name = name
        break

mic = sr.Microphone(device_index=mic_index)
speak(f"Jarvis online.")

# ---------- FOLDER LOCATIONS TO SEARCH ----------
home = os.path.expanduser("~")
SEARCH_DIRECTORIES = [
    os.path.join(home, "Desktop"),
    os.path.join(home, "Downloads"),
    os.path.join(home, "Documents"),
    r"C:\Program Files",
    r"C:\Program Files (x86)",
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

            try:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        try:
                            f_lower = file.lower()
                            if f_lower.endswith(INDEX_EXTENSIONS):
                                name_key = os.path.splitext(f_lower)[0]
                                full_path = os.path.join(root, file)
                                if name_key not in FILE_INDEX:
                                    FILE_INDEX[name_key] = full_path
                        except Exception as e:
                            print(f"Error indexing file {file}: {e}")
                            continue
            except Exception as e:
                print(f"Error walking directory {directory}: {e}")
                continue

        print(f"Indexed {len(FILE_INDEX)} items.")
        speak("right Cas. How we fixing the system today.")
    except Exception as e:
        print(f"Critical error building file index: {e}")

# Build the index once at startup (this is the “one line” you add)
build_file_index()

# ---------- UPDATED OPEN FUNCTION (uses index) ----------
def open_program(name: str):
    try:
        name = name.lower().strip()
        if not name:
            speak("No program specified.")
            return False

        # alias normalize
        name = ALIASES.get(name, name)

        # predefined direct paths first
        if name in PROGRAM_PATHS:
            program_path = PROGRAM_PATHS[name]
            if os.path.exists(program_path) or program_path.startswith("http"):
                speak(f"Opening {name}.")
                print(f"Trying to open {program_path}")
                try:
                    os.system(f'start "" "{program_path}"')
                    return True
                except Exception as e:
                    print(f"Error launching {program_path}: {e}")
                    speak(f"Error opening {name}.")
                    return False
            else:
                speak(f"Program path not found: {program_path}")
                return False

        # exact indexed lookup (fast)
        if name in FILE_INDEX:
            program_path = FILE_INDEX[name]
            if os.path.exists(program_path):
                speak(f"Opening {name}.")
                print(f"Opening {program_path}")
                try:
                    os.system(f'start "" "{program_path}"')
                    return True
                except Exception as e:
                    print(f"Error launching {program_path}: {e}")
                    return False
            else:
                print(f"File no longer exists: {program_path}")
                return False

        # partial match fallback
        for key in FILE_INDEX:
            if name in key:
                program_path = FILE_INDEX[key]
                if os.path.exists(program_path):
                    speak(f"Opening {key}.")
                    print(f"Opening {program_path}")
                    try:
                        os.system(f'start "" "{program_path}"')
                        return True
                    except Exception as e:
                        print(f"Error launching {program_path}: {e}")
                        return False

        speak(f"I couldn't find {name}.")
        return False
    except Exception as e:
        print(f"Error in open_program: {e}")
        speak("An error occurred while opening the program.")
        return False
# Hidden: Created by C.a.s.s If you found this Call the number! - (+44) 7512189347
# ---------- COMMAND PARSER / ROUTER ----------
VERB_OPEN = {"open", "launch", "start", "run"}
VERB_HELP = {"help", "commands", "what can you do", "list commands"}
VERB_SHUTDOWN = {"shutdown", "shut down", "close", "close assistant", "quit", "exit", "stop", "end"}
VERB_VOLUME = {"set volume", "adjust volume", "volume"}
VERB_FILE = {"open file", "save file", "open folder"}
VERB_REMIND = {"remind me", "set reminder"}

def route_command(command_clean: str):
    c = normalize_text(command_clean)

    # shutdown
    for k in VERB_SHUTDOWN:
        if k in c:
            speak("Adios.")
            return "shutdown", None

    # volume control
    for k in VERB_VOLUME:
        if k in c:
            volume_level = extract_volume_level(c)  # Custom function to extract volume
            adjust_volume(volume_level)
            return "volume", volume_level

    # file management
    for k in VERB_FILE:
        if k in c:
            file_action = extract_file_action(c)  # Extract file-related action (open/save)
            handle_file_action(file_action)
            return "file", file_action

    # reminder
    for k in VERB_REMIND:
        if k in c:
            reminder_time = extract_reminder_time(c)  # Extract reminder time
            set_reminder(reminder_time)
            return "reminder", reminder_time

    # open/launch/start/run + target
    tokens = c.split(" ")
    if tokens and tokens[0] in VERB_OPEN:
        target = c[len(tokens[0]):].strip().strip(" .")
        if target:
            return "open", target

    return "none", None
    
def normalize_text(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t

def strip_wakeword(t: str) -> str:
    return t.replace("jarvis", "").strip()

def route_command(command_clean: str):
    c = normalize_text(command_clean)

    # shutdown
    for k in VERB_SHUTDOWN:
        if k in c:
            speak("Adios.")
            return "shutdown", None

    # help
    if any(k in c for k in VERB_HELP):
        speak("Commands: say Jarvis open plus an app name. Say Jarvis shutdown to close.")
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
                print(".", end="", flush=True)  # heartbeat every timeout
                continue
            except sr.RequestError as e:
                print(f"Microphone/API error: {e}")
                speak("Microphone error. Please check your audio.")
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
        
        # Start greeting in background thread (non-blocking)
        def greet():
            speak("What's up Cass?")
        greeting_thread = threading.Thread(target=greet, daemon=True)
        greeting_thread.start()

        # ACTIVE LISTEN (real command)
        with mic as source:
            print("Listening for command...")
            try:
                command_audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                speak("Timed out.")
                continue
            except sr.RequestError as e:
                print(f"Microphone error: {e}")
                speak("Microphone error.")
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
        time.sleep(1)  # Avoid rapid error loops
        continue