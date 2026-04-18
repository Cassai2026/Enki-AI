 # If you see 'Import "speech_recognition" could not be resolved', install it via:
 # pip install SpeechRecognition
import speech_recognition as sr
import time
import re
import webbrowser
import keyboard
import subprocess
import os
import threading
import pyautogui  # Required for simulating keyboard actions to control volume
import re

# Function to extract the volume level from the command
def extract_volume_level(command):
    """Extract volume level from command like 'set volume to 50%'."""
    volume_level = None
    if "volume" in command and "%" in command:
        volume_level = int(''.join(filter(str.isdigit, command)))  # Extract digits as volume
    return volume_level

# Function to adjust the system volume (this simulates pressing volume keys)
def adjust_volume(level):
    """Adjust system volume to the desired level."""
    if level is None or level < 0 or level > 100:
        print("Invalid volume level.")
        return

    # Using pyautogui to simulate pressing volume keys (for Windows)
    print(f"Setting volume to {level}%")
    pyautogui.hotkey('volumedown', presses=(100 - level) // 2)  # Adjust volume
# ---------- VOICE SETUP ----------engine = pyttsx3.init()

def speak(text: str):
    # Windows built-in TTS via PowerShell (stable)
    safe = text.replace('"', "'")
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f'Add-Type -AssemblyName System.Speech; '
            f'$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            f'$speak.Rate = 1; '
            f'$speak.Speak("{safe}");'
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
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
speak(f"Jarvis online. Using microphone: {mic_name or 'default'}")

# ---------- FOLDER LOCATIONS TO SEARCH ----------
SEARCH_DIRECTORIES = [
    r"C:\Users\pcass\Desktop",
    r"C:\Users\pcass\Downloads",
    r"C:\Users\pcass\Documents",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Users\pcass\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc"
]

# ---------- FIXED PROGRAM LAUNCH PATHS ----------
PROGRAM_PATHS = {
    "wow": r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": r"C:\Users\pcass\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk",
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
    # speak("Building file index. Please wait.")  # uncomment if you want voice notice

    for directory in SEARCH_DIRECTORIES:
        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            for file in files:
                f_lower = file.lower()
                if f_lower.endswith(INDEX_EXTENSIONS):
                    name_key = os.path.splitext(f_lower)[0]
                    full_path = os.path.join(root, file)
                    if name_key not in FILE_INDEX:
                        FILE_INDEX[name_key] = full_path

    print(f"Indexed {len(FILE_INDEX)} items.")
    speak("Index complete.")

# Build the index once at startup (this is the “one line” you add)
build_file_index()

# ---------- UPDATED OPEN FUNCTION (uses index) ----------
def open_program(name: str):
    name = name.lower().strip()

    # alias normalize
    name = ALIASES.get(name, name)

    # predefined direct paths first
    if name in PROGRAM_PATHS:
        program_path = PROGRAM_PATHS[name]
        speak(f"Opening {name}.")
        print(f"Trying to open {program_path}")
        os.system(f'start "" "{program_path}"')
        return True

    # exact indexed lookup (fast)
    if name in FILE_INDEX:
        speak(f"Opening {name}.")
        print(f"Opening {FILE_INDEX[name]}")
        os.system(f'start "" "{FILE_INDEX[name]}"')
        return True

    # partial match fallback
    for key in FILE_INDEX:
        if name in key:
            speak(f"Opening {key}.")
            print(f"Opening {FILE_INDEX[key]}")
            os.system(f'start "" "{FILE_INDEX[key]}"')
            return True

    speak(f"I couldn't find {name}.")
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

        try:
            wake_text = recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            continue
        except Exception:
            continue

        if "jarvis" not in wake_text:
            continue

        print("Wake word detected.")
        
        # Start greeting in background thread (non-blocking)
        def greet():
            speak("what's up cass?")
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

        try:
            command = recognizer.recognize_google(command_audio).lower()
            print("Command:", command)
        except sr.UnknownValueError:
            speak("I didn't catch that.")
            continue
        except Exception:
            speak("Speech error.")
            continue

        action, payload = route_command(command)

        if action == "shutdown":
            break

        if action == "help":
            continue

        if action == "open" and payload:
            open_program(payload)

    except Exception as e:
        print("Error:", e)
        continue